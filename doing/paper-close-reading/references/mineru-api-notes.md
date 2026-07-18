# MinerU API Notes

来源：https://mineru.net/apiManage/docs

## 精准解析 API

本地文件使用批量上传链路：

1. `POST https://mineru.net/api/v4/file-urls/batch`
2. 用返回的预签名 URL 执行 `PUT` 上传本地文件字节；上传时无需设置 `Content-Type`
3. `GET https://mineru.net/api/v4/extract-results/batch/{batch_id}` 轮询结果
4. `state=done` 后下载 `full_zip_url`

认证头：

```text
Authorization: Bearer <token>
```

本工作区 token 默认来自 `.env` 的 `minerU_API`。

## 推荐参数

- `model_version`: `vlm`
- `enable_formula`: `true`
- `enable_table`: `true`
- `language`: `ch`
- `file.is_ocr`: 扫描版才设为 `true`

## 状态处理

继续轮询：

- `waiting-file`
- `pending`
- `running`
- `converting`

成功：

- `done` 且存在 `full_zip_url`

失败：

- `failed`，展示 `err_msg`

## 常见错误

- `A0202`：Token 错误，检查 Bearer token 和 `.env`
- `A0211`：Token 过期
- `-60005`：文件超过 200 MB
- `-60006`：页数超过 200 页
- `-60007`：模型服务暂时不可用
- `-60009`：任务队列已满
- `-60010`：解析失败
- `-60012`：任务不存在
