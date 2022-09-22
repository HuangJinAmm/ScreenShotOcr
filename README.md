截屏ocr小工具

采用python中的 pyqt5+paddleocr+opencv写的一个单机版的截屏识别小工具。可以识别表格和布局。识别后数据会放在剪切板，然后就可以快乐的ctrl+V了，表格数据可以在excel里直接ctrl+V。（想用其他ocr的可看看这个[Tesseract OCR Engine](https://github.com/tesseract-ocr/tesseract)）

- **截图识别文字:** 识别文字。切会按照布局位置添加缩进。（这个也可以识别简单的表格数据，识别后的数据的列用“\t“隔开）。  

- **识别表格：** 可以识别表格和布局。这个paddleocr自带的实现。可以识别合并的单元格。

- **识别关键信息：** 埋个坑先。

运行步骤：

1. 安装python环境。我用的python3.8。
2. pip install -r requirements.txt  -i https://pypi.tuna.tsinghua.edu.cn/simple
3. python main.py

动机：

    作为一位资深cv(ctrl+CV)工程师，在博客时copy代码时。经常会有些代码图片、或者就是网页限制不让复制。故开发这个小工具。虽然准确率一般。但是又不是不能用。

![13.gif](.\res\13.gif)

![12.gif](D:\2-learn\python\ScreenShotOcr\res\12.gif)
