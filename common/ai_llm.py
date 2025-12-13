import os
import dashscope
from http import HTTPStatus

# # def DeepSeekAli(messages):
# # 通过 messages 数组实现上下文管理
# messages = [
#     {'role': 'user', 'content': '你是最新数据截止到什么时候？'}
# ]

# response = dashscope.Generation.call(
#     api_key="sk-554daaf988c34abfbc7073fa4b3bb433",
#     model="qwen-omni-turbo",
#     messages=messages,
#     result_format='message'
# )

# print("=" * 20 + "第一轮对话" + "=" * 20)
# print("=" * 20 + "思考过程" + "=" * 20)
# print(response.output.choices[0].message.reasoning_content)
# print("=" * 20 + "最终答案" + "=" * 20)
# print(response.output.choices[0].message.content)


def call_deepseek(messages, llm):
    response = dashscope.Generation.call(
        api_key=llm.api_key,
        model=llm.model_code,
        messages=messages,
        result_format='message',  # set the result to be "message" format.
    )
    if response.status_code == HTTPStatus.OK:
        return response.output.choices[0].message.content
    else:
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))
