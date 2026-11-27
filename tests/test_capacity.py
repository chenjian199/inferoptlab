import unittest

from benchmark.load.capacity import concurrency_points, glm_slot_blocks, rank_limit


class CapacityTests(unittest.TestCase):
    def test_clamp_deduplicates_and_recounts_requests(self):
        result = concurrency_points([1, 2, 4, 8, 16, 32, 64, 128], [3] * 8)
        self.assertEqual(result['capacity_limit'], 24)
        self.assertEqual([p['concurrency'] for p in result['points']], [1, 2, 4, 8, 16, 24])
        self.assertEqual(result['points'][-1]['requests'], 96)
        self.assertEqual(result['points'][-1]['slots_per_rank'], [3] * 8)

    def test_rank16_is_not_global16(self):
        self.assertEqual(concurrency_points([128], [16] * 8)['capacity_limit'], 128)

    def test_sticky_routing_does_not_sum_unequal_capacity(self):
        self.assertEqual(concurrency_points([8], [1, 2])['capacity_limit'], 2)
        self.assertEqual(concurrency_points([8], [2, 1])['capacity_limit'], 3)

    def test_zero_capacity_yields_no_timing_points(self):
        self.assertEqual(concurrency_points([1, 4], [0, 8])['points'], [])

    def test_scheduler_limit_does_not_clip_resident_capacity(self):
        # Synthetic arithmetic, not a claim about measured GLM group costs.
        pool = dict(total_blocks=101, reserved_blocks=1, blocks_per_slot=20)
        self.assertEqual(rank_limit(pools=[pool], max_num_seqs=16,
                                   max_num_batched_tokens=2048)['kv_limit'], 5)
        self.assertEqual(rank_limit(pools=[pool], max_num_seqs=3,
                                   max_num_batched_tokens=2048)['kv_limit'], 5)
        self.assertEqual(rank_limit(pools=[pool], max_num_seqs=16,
                                   max_num_batched_tokens=2)['scheduling_limit'], 2)
        pool['blocks_per_slot'] = 26
        self.assertEqual(rank_limit(pools=[pool], max_num_seqs=16,
                                   max_num_batched_tokens=2048)['kv_limit'], 3)

    def test_scan_uses_kv_budget_even_with_waiting_requests(self):
        limits = rank_limit(pools=[dict(total_blocks=1001, reserved_blocks=1,
                                      blocks_per_slot=10)],
                            max_num_seqs=16, max_num_batched_tokens=2048)
        result = concurrency_points([16, 32, 64, 128], [limits['kv_limit']])
        self.assertEqual([p['concurrency'] for p in result['points']], [16, 32, 64, 100])

    def test_glm_formula_reserves_seed_output_and_original_prefix(self):
        budget = glm_slot_blocks(4096, 512, 4352)
        self.assertEqual(budget['attention_blocks'], 2)
        self.assertEqual(budget['runtime_model_blocks'], 11)
        self.assertEqual(budget['reserved_slot_blocks'], 16)

    def test_separate_pools_use_minimum(self):
        pools = [dict(total_blocks=101, reserved_blocks=1, blocks_per_slot=20),
                 dict(total_blocks=41, reserved_blocks=1, blocks_per_slot=20)]
        self.assertEqual(rank_limit(pools=pools, max_num_seqs=16,
                                   max_num_batched_tokens=2048)['kv_limit'], 2)

    def test_missing_or_invalid_evidence_is_not_capacity(self):
        for pools in [[], [dict(total_blocks=10, reserved_blocks=1, blocks_per_slot=0)],
                      [dict(total_blocks=0, reserved_blocks=1, blocks_per_slot=1)]]:
            with self.assertRaises(ValueError):
                rank_limit(pools=pools, max_num_seqs=16, max_num_batched_tokens=2048)
        with self.assertRaises(ValueError):
            concurrency_points([True], [16])

    def test_routing_formula_matches_exhaustive_placement(self):
        for limits in ([0], [2], [1, 4], [4, 1], [2, 3, 1], [2] * 8):
            expected = 0
            for c in range(sum(limits) + 1):
                loads = [sum(s % len(limits) == r for s in range(c)) for r in range(len(limits))]
                if all(a <= b for a, b in zip(loads, limits)):
                    expected = c
            self.assertEqual(concurrency_points([128], limits)['capacity_limit'], expected)


if __name__ == '__main__':
    unittest.main()
