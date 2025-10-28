import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import statistics

class PressureTester:
    """
    压力测试类，用于测试Web服务的性能
    """
    
    def __init__(self, base_url: str):
        """
        初始化压力测试器
        
        Args:
            base_url: 服务器基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        
    def single_request(self, endpoint: str) -> Dict:
        """
        发送单个HTTP请求并记录响应时间
        
        Args:
            endpoint: 请求的端点
            
        Returns:
            包含请求结果和响应时间的字典
        """
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}{endpoint}")
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            return {
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "success": response.status_code == 200,
                "error": None
            }
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                "status_code": None,
                "response_time_ms": response_time,
                "success": False,
                "error": str(e)
            }
    
    def concurrent_test(self, endpoint: str, concurrent_users: int, requests_per_user: int) -> List[Dict]:
        """
        并发测试
        
        Args:
            endpoint: 测试端点
            concurrent_users: 并发用户数
            requests_per_user: 每个用户的请求数
            
        Returns:
            所有请求的结果列表
        """
        results = []
        
        # 使用线程池执行并发请求
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            # 提交所有任务
            futures = []
            for _ in range(concurrent_users * requests_per_user):
                future = executor.submit(self.single_request, endpoint)
                futures.append(future)
            
            # 收集结果
            for future in as_completed(futures):
                results.append(future.result())
                
        return results
    
    def pressure_test(self, endpoint: str, concurrent_users: int, requests_per_user: int) -> Dict:
        """
        执行压力测试并生成报告
        
        Args:
            endpoint: 测试端点
            concurrent_users: 并发用户数
            requests_per_user: 每个用户的请求数
            
        Returns:
            压力测试报告
        """
        print(f"开始压力测试: {endpoint}")
        print(f"并发用户数: {concurrent_users}, 每用户请求数: {requests_per_user}")
        
        start_time = time.time()
        results = self.concurrent_test(endpoint, concurrent_users, requests_per_user)
        end_time = time.time()
        
        total_time = end_time - start_time
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r["success"])
        failed_requests = total_requests - successful_requests
        
        # 计算响应时间统计
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
        """
        打印压力测试报告
        
        Args:
            report: 压力测试报告
        """
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

def main():
    """
    主函数 - 执行压力测试示例
    """
    # 根据你的server.py配置相应的URL
    tester = PressureTester("http://127.0.0.1:3000")
    
    # 测试
    report = tester.pressure_test("/user", concurrent_users=50, requests_per_user=50)
    tester.print_report(report)
    
    print("\n" + "="*50)
    print("详细错误信息 (如果有)")
    print("="*50)
    
    # 显示前5个失败请求的错误信息
    failed_results = [r for r in report["raw_results"] if not r["success"]]
    for i, result in enumerate(failed_results[:5]):
        print(f"错误 {i+1}: {result['error']}")

if __name__ == "__main__":
    main()