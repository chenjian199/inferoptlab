import unittest

from benchmark.breakdown.torch_trace import summarize_events


class TorchTraceTests(unittest.TestCase):
    def test_device_overlap_cpu_inclusion_and_rank_isolation(self):
        def event(cat,name,ts,dur,device=0):
            return dict(ph='X',cat=cat,name=name,ts=ts,dur=dur,pid=9,args=dict(device=device))
        result=summarize_events([event('kernel','gemm',0,1000),event('kernel','gemm',500,1000),
            event('kernel','gemm',0,4000,1),event('cpu_op','aten::mm',0,7000),event('cuda_runtime','cudaGraphLaunch',0,10)])
        self.assertEqual(result['lanes']['0']['kernel_interval_union_ms'],1.5)
        self.assertEqual(result['lanes']['0']['kernel_duration_sum_ms'],2)
        self.assertEqual(result['lanes']['1']['kernel_interval_union_ms'],4)
        self.assertEqual(result['graph_replay_events'],{'cudaGraphLaunch':1})
        self.assertEqual(sum(r['calls'] for r in result['operators'] if r['kind']=='gpu_kernel'),3)

    def test_cpu_only_trace_is_not_device_work(self):
        result=summarize_events([dict(ph='X',cat='cpu_op',name='aten::mm',ts=0,dur=200,pid=1)])
        self.assertFalse(result['lanes'])
        self.assertEqual(result['operators'][0]['kind'],'cpu_op')

    def test_gpu_annotation_copies_do_not_inflate_iteration_count(self):
        name='execute_context_0(0)_generation_1(1)'
        rows=[dict(ph='X',cat=cat,name=name,ts=0,dur=100,pid=1)
              for cat in ['user_annotation','gpu_user_annotation','gpu_user_annotation']]
        self.assertEqual(summarize_events(rows)['annotations'],{name:1})


if __name__=='__main__':unittest.main()
