# async_pressure.py
import asyncio
import time
import statistics
from typing import List, Dict

import httpx
from tqdm import tqdm


class AsyncPressureTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def _single_request(self, client: httpx.AsyncClient, endpoint: str, sem: asyncio.Semaphore) -> Dict:
        async with sem:
            start = time.perf_counter()
            try:
                resp = await client.get(f"{self.base_url}{endpoint}")
                elapsed_ms = (time.perf_counter() - start) * 1000
                return {
                    "status_code": resp.status_code,
                    "response_time_ms": elapsed_ms,
                    "success": resp.status_code == 200,
                    "error": None
                }
            except Exception as e:
                elapsed_ms = (time.perf_counter() - start) * 1000
                return {
                    "status_code": None,
                    "response_time_ms": elapsed_ms,
                    "success": False,
                    "error": str(e)
                }

    async def concurrent_test(self, endpoint: str, concurrent_users: int, requests_per_user: int) -> List[Dict]:
        total_requests = concurrent_users * requests_per_user
        sem = asyncio.Semaphore(concurrent_users)  # 限制并发
        results: List[Dict] = []
        success_count = 0

        # 配置连接上限，避免打开过多连接（根据需要调整）
        limits = httpx.Limits(max_connections=concurrent_users * 2, max_keepalive_connections=concurrent_users)

        async with httpx.AsyncClient(limits=limits, timeout=30.0) as client:
            # 创建 tasks（立即 schedule）
            tasks = [asyncio.create_task(self._single_request(client, endpoint, sem)) for _ in range(total_requests)]

            # 用 tqdm + asyncio.as_completed 正确显示进度
            ac = asyncio.as_completed(tasks)
            with tqdm(total=total_requests, desc="压力测试进度", unit="req") as pbar:
                for future in ac:
                    res = await future
                    results.append(res)
                    if res["success"]:
                        success_count += 1

                    # 更新进度栏（用增量计数避免重复扫描结果列表）
                    completed = len(results)
                    success_rate = (success_count / completed * 100) if completed > 0 else 0.0
                    pbar.set_postfix({"并发数": concurrent_users, "成功率": f"{success_rate:.2f}%"})
                    pbar.update(1)

        return results

    async def pressure_test(self, endpoint: str, concurrent_users: int, requests_per_user: int) -> Dict:
        print(f"开始压力测试: {endpoint}")
        print(f"并发用户数: {concurrent_users}, 每用户请求数: {requests_per_user}")

        start_time = time.time()
        results = await self.concurrent_test(endpoint, concurrent_users, requests_per_user)
        end_time = time.time()

        total_time = end_time - start_time
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r["success"])
        failed_requests = total_requests - successful_requests

        response_times = [r["response_time_ms"] for r in results if r["success"]]

        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            median_response_time = statistics.median(response_times)
        else:
            avg_response_time = min_response_time = max_response_time = median_response_time = 0

        success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0

        report = {
            "test_info": {
                "endpoint": endpoint,
                "concurrent_users": concurrent_users,
                "requests_per_user": requests_per_user,
                "total_requests": total_requests
            },
            "results": {
                "total_time_seconds": round(total_time, 2),
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": round(success_rate, 2)
            },
            "response_time_stats": {
                "average_ms": round(avg_response_time, 2),
                "min_ms": round(min_response_time, 2),
                "max_ms": round(max_response_time, 2),
                "median_ms": round(median_response_time, 2)
            },
            "raw_results": results
        }
        return report

    def print_report(self, report: Dict) -> None:
        info = report["test_info"]
        results = report["results"]
        response_stats = report["response_time_stats"]

        print("\n" + "="*50)
        print("压力测试报告")
        print("="*50)
        print(f"测试端点: {info['endpoint']}")
        print(f"并发用户数: {info['concurrent_users']}")
        print(f"每用户请求数: {info['requests_per_user']}")
        print(f"总请求数: {info['total_requests']}")
        print("-"*50)
        print(f"总耗时: {results['total_time_seconds']} 秒")
        print(f"成功请求数: {results['successful_requests']}")
        print(f"失败请求数: {results['failed_requests']}")
        print(f"成功率: {results['success_rate']}%")
        print("-"*50)
        print(f"平均响应时间: {response_stats['average_ms']} ms")
        print(f"最小响应时间: {response_stats['min_ms']} ms")
        print(f"最大响应时间: {response_stats['max_ms']} ms")
        print(f"中位响应时间: {response_stats['median_ms']} ms")
        print("="*50)


async def main():
    tester = AsyncPressureTester("http://127.0.0.1:3000")
    report = await tester.pressure_test("/health", concurrent_users=50, requests_per_user=100)
    tester.print_report(report)

    print("\n" + "="*50)
    print("详细错误信息 (如果有)")
    print("="*50)
    failed_results = [r for r in report["raw_results"] if not r["success"]]
    for i, result in enumerate(failed_results[:5]):
        print(f"错误 {i+1}: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())
