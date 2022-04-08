## Cropper Tool

## Introduction

The CropperTool.py can be used to seperate the single rectangles of the game board image. This is usefull to recognize multiple objects in one image.
The rectangular shapes are found by looking for red dots on the board game and analysing the relative position. 

## Table of Contents

1. [Introduction](#Introdurction)
2. [How to use](#Howtouse)
   1. [Class Description](#ClassDescription)
   2. [Usage](#Usage)
3. [Contributing](#Contributing)
4. [Links](#Links)

## How to use

### Class Description

* **Grid** **`ShapeAnalysis.py`**
  Main Features:

  * specialized for a 5x2 rectangle board = 3x6 red dots
  * use the identified red dot coorditates to determine single rectangles
  * calculate missing dots out of the information
  * delete not useful dots
* **StraightLineEquation** **`StraightLineEquation.py`**
  Main Features:

  * a mathematical straight line equation $f(x)=a\cdot x + b$
  * can be used to find horizontal related dot coordintates

### Usage

Write the file name for the to cropping image into the `CropperTool.py` file.

```python
# =========================================================================== #
#  SECTION: Global definitions
# =========================================================================== #
FILENAME = "Testbilder\photo_test6.jpg"
```

Execute the `Cropper.py` file and especially the `seperate_the_objects()` method. The board game image will be seperated into single rectangular images. The consecutively numbered `roi*.jpg` images can be found in the folder `cutouts`.


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Links

Helpfull links:

* [all the answers](https://www.google.de/search?q=how+to+use+google&sxsrf=ALeKk01Pw_bxWGHPxYMFQxHBGvFGsr2o-Q%3A1624293592793&source=hp&ei=2MDQYOeDLsSAaaKmo8AH&iflsig=AINFCbYAAAAAYNDO6AEUucQ4syTqAp9GA4a02F4ETKfn&oq=how+to+use+google&gs_lcp=Cgdnd3Mtd2l6EAMyBQgAEMsBMgUIABDLATIFCAAQywEyBQgAEMsBMgUIABDLATIFCAAQywEyBQgAEMsBMgUIABDLATIFCAAQywEyBQgAEMsBOgcIIxDqAhAnOgQIIxAnOggIABDHARCjAjoCCAA6AgguOgUILhDLAVCG8ghY0oUJYKuHCWgBcAB4AIABwQGIAekLkgEEMTYuMZgBAKABAaoBB2d3cy13aXqwAQo&sclient=gws-wiz&ved=0ahUKEwjnz-2UlanxAhVEQBoKHSLTCHgQ4dUDCAk&uact=5)
