from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
from src.article_generator import article_generator
from src.style_manager import style_manager
from src.config import config
from src.model_provider import ModelProviderFactory, model_provider

# 创建FastAPI应用
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="AI写作助手，支持多种写作风格"
)

# 配置模板
templates = Jinja2Templates(directory="frontend/templates")
# 禁用模板缓存以避免unhashable type错误
templates.env.cache = None

# 定义请求模型


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200, description="文章主题")
    style: str = Field("creative", min_length=1,
                       max_length=50, description="写作风格")
    length: str = Field(
        "medium", pattern="^(short|medium|long)$", description="文章长度")
    title: Optional[str] = Field(None, max_length=100, description="文章标题")


class ModelProviderRequest(BaseModel):
    provider: str = Field(..., pattern="^(openai|ollama)$", description="模型提供者")

# 根路径


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html")

# 生成文章


@app.post("/generate")
def generate_article(request: GenerateRequest):
    try:
        # 生成标题（如果没有提供）
        if not request.title:
            title = article_generator.generate_title(
                request.topic, request.style)
        else:
            title = request.title

        # 生成内容
        content = article_generator.generate_content(
            request.topic,
            request.style,
            request.length,
            title
        )

        return {"title": title, "content": content}
    except Exception as e:
        # 打印错误信息到日志
        print(f"Error generating article: {e}")
        # 避免泄露内部错误详情
        raise HTTPException(status_code=500, detail="文章生成失败，请稍后重试")

# 流式生成文章


@app.post("/stream")
def stream_article(request: GenerateRequest):
    def generate():
        try:
            # 生成标题（如果没有提供）
            if not request.title:
                title = article_generator.generate_title(
                    request.topic, request.style)
            else:
                title = request.title

            # 转义标题中的特殊字符
            escaped_title = title.replace("\"", "\\\"")
            escaped_title = escaped_title.replace("\n", "\\n")

            # 流式生成内容
            yield f"{{\"title\": \"{escaped_title}\", \"content\": \""

            for chunk in article_generator.stream_content(
                request.topic,
                request.style,
                request.length,
                title
            ):
                # 转义特殊字符
                chunk = chunk.replace("\"", "\\\"")
                chunk = chunk.replace("\n", "\\n")
                yield chunk

            yield f"\"}}"
        except Exception as e:
            # 避免泄露内部错误详情
            yield f"{{\"error\": \"文章生成失败，请稍后重试\"}}"

    return StreamingResponse(generate(), media_type="application/json")


# 模型提供者管理


@app.get("/model/provider")
def get_current_provider():
    """获取当前模型提供者"""
    return {"current_provider": config.MODEL_PROVIDER}


@app.post("/model/provider")
def set_model_provider(request: ModelProviderRequest):
    """设置模型提供者"""
    try:
        # 更新全局配置
        config.MODEL_PROVIDER = request.provider
        # 更新全局模型提供者实例
        global model_provider
        model_provider = ModelProviderFactory.get_provider(request.provider)
        return {"message": f"模型提供者已切换为 {request.provider}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="切换模型提供者失败")


# 运行应用
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
