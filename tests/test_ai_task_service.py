import pytest
import asyncio
from unittest.mock import Mock, patch

try:
    import asyncpg  # type: ignore
except ImportError:
    pytest.skip("asyncpg not installed; skipping ai task service tests", allow_module_level=True)

from services.ai_task_service import AITaskService

@pytest.fixture
def mock_db_manager():
    """创建模拟数据库管理器"""
    return Mock()

@pytest.fixture
def mock_llm_fetcher():
    """创建模拟LLM获取器"""
    return Mock()

@pytest.fixture
def ai_task_service(mock_db_manager, mock_llm_fetcher):
    """创建AI任务服务实例"""
    return AITaskService(mock_db_manager, mock_llm_fetcher)

def test_init(ai_task_service, mock_db_manager, mock_llm_fetcher):
    """测试AI任务服务初始化"""
    assert ai_task_service.db_manager == mock_db_manager
    assert ai_task_service.llm_fetcher == mock_llm_fetcher

@patch('services.ai_task_service.uuid')
def test_save_ai_request(mock_uuid, ai_task_service):
    """测试保存AI请求记录"""
    # 设置模拟返回值
    mock_uuid.uuid4.return_value = 'test-uuid'
    mock_conn = Mock()
    ai_task_service.db_manager.get_connection = Mock(return_value=asyncio.Future())
    ai_task_service.db_manager.get_connection.return_value.set_result(mock_conn)
    ai_task_service.db_manager.release_connection = Mock(return_value=asyncio.Future())
    ai_task_service.db_manager.release_connection.return_value.set_result(None)
    
    # 调用测试方法
    asyncio.run(ai_task_service._save_ai_request('user123', 'test prompt', 'test response'))
    
    # 验证调用
    mock_conn.execute.assert_called_once()
    ai_task_service.db_manager.release_connection.assert_called_once_with(mock_conn)

# 运行测试的示例命令：
# python -m pytest tests/test_ai_task_service.py -v
