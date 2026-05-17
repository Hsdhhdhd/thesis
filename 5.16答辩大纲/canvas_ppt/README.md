# 5.16 答辩大纲 Canvas PPT

这是一个基于 HTML Canvas 绘制的硕士论文答辩演示文稿，放在 `5.16答辩大纲/canvas_ppt` 下，主要使用 `5.16答辩大纲` 的答辩结构和 `5.12论文重写/images` 的论文图片素材。

- `5.16答辩大纲/25分钟答辩PPT详尽大纲_完全贴合论文版.md`：作为 22 页主讲 + 6 页 backup 的内容结构来源。
- `5.12论文重写/images/`：作为主要图片素材来源。
- `5.17ppt整理/02_图片素材/生成图片_image2_可选/`：作为概念图补充来源。

## 怎么看

推荐从仓库根目录启动一个本地服务器；这样图片加载和 PNG 导出都走同源 HTTP，最稳定：

```bash
cd /workspace/thesis
python3 -m http.server 8000
```

然后在浏览器打开：

```text
http://localhost:8000/canvas_ppt/
```

如果在本地 Windows 仓库中打开这一份，推荐从 `D:\最终论文` 启动服务器：

```powershell
cd D:\最终论文
python -m http.server 8000 --bind 127.0.0.1
```

然后打开：

```text
http://127.0.0.1:8000/5.16%E7%AD%94%E8%BE%A9%E5%A4%A7%E7%BA%B2/canvas_ppt/
```

不推荐直接双击 `index.html`：部分浏览器会因为本地 `file://` 图片安全策略导致 PNG 导出失败。

## 操作

- `←` / `→`：上一页 / 下一页
- `F`：全屏
- `E`：导出当前页 PNG
- 右侧缩略图：快速跳转到任意页面

## 本地检查

不用浏览器也可以先检查 HTML、内联 JavaScript、slide 数量和 5.17 图片路径：

```bash
cd /workspace/thesis
python3 5.16答辩大纲/canvas_ppt/validate_canvas_ppt.py
```

## 页面结构

当前版本共 28 页：

- 22 页主讲 slides
- 6 页 backup slides

整体内容对应 5.17 整理文件夹中的 25 分钟答辩大纲。
