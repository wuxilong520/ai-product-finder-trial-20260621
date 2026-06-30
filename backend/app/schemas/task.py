from pydantic import BaseModel, Field


class TaskSubmitRequest(BaseModel):
    keyword: str = Field(..., min_length=1, description="任务关键词")
    market_type: str = Field(..., min_length=1, description="市场类型")
    supplier_strategy: str = Field(..., min_length=1, description="供应策略")
    cost_mode: str = Field(..., min_length=1, description="成本模式")
    decision_mode: str = Field(..., min_length=1, description="决策模式")
