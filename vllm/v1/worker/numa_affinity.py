import os

def set_numa_affinity_for_gpu(gpu_id):
    """
    将当前进程CPU亲和性绑定到和指定GPU同属的NUMA节点。
    仅支持Linux+NVIDIA。
    """
    # 1. 查询GPU所属NUMA节点
    numa_path = f"/sys/class/drm/card{gpu_id}/device/numa_node"
    try:
        with open(numa_path) as f:
            numa_node = int(f.read())
        if numa_node < 0:
            # -1 表示未知/单节点，跳过设置
            return
    except Exception:
        return

    # 2. 查询该NUMA节点下所有CPU核心
    cpulist_path = f"/sys/devices/system/node/node{numa_node}/cpulist"
    try:
        with open(cpulist_path) as f:
            cpulist_str = f.read().strip()
        # 格式例: '0-15,32-47'
        cpu_ids = []
        for part in cpulist_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                cpu_ids.extend(range(start, end+1))
            else:
                cpu_ids.append(int(part))
    except Exception:
        return

    # 3. 设置进程CPU亲和性
    try:
        os.sched_setaffinity(0, cpu_ids)
    except Exception:
        pass
