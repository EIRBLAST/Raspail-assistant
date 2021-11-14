from PIL import Image, ImageDraw, ImageFont

def get_color(name: str) -> str:
    """Return a color corresponding to the subject.

    Args:
        name (str): Name of the subject.

    Returns:
        str: The color as html color code.
    """
    colors = {"Physique-Chimie": "Thistle", "Maths": "PaleGreen", "Anglais": "PowderBlue", "S2I": "LemonChiffon", "Français": "LightPink",
              "Informatique": "LightCyan", "DS": "red", "colle": "grey", "TIPE": "Tan", "tp": "LemonChiffon"}

    return colors.get(name, "#D5D8DC")

class timtable_imager():
    def __init__(self, time_range : tuple = (8, 19) , **kwargs) -> None:
        self.block_dimention = {
            "width": 300,
            "height": 100
        }

        # TODO: delete `**kwargs` and use defined arguments
        # Refer to line #97

        self.timetable_dimention = {
            "width": kwargs.get("timetable_dimention_width", 7),
            "height": kwargs.get("timetable_dimention_height", time_range[1] - time_range[0] + 1)
        }

        # END TODO

        #self.canvas = Image.new('RGB', (self.image_dimention["width"], self.image_dimention["width"]*self.timetable_dimention["height"]), color = 'white')

        self.time_range = time_range

        self.fonts = {
            "regular": ImageFont.truetype('datas/Roboto-Regular.ttf', self.block_dimention["height"]//5),
            "bold": ImageFont.truetype('datas/Roboto-Bold.ttf', self.block_dimention["height"]//4)
        }

    def generate_block(self, lines: dict, height: int = 1, color: str = "grey") -> Image.Image:
        """Generate a block of the timetable as an image.

        Args:
            lines (dict): Lines of text to be printed in the block.
            height (int, optional): Height of the block in block unite. Defaults to 1.
            color (str, optional): Color of the block. Defaults to "grey".

        Returns:
            Image.Image: The generated block.
        """        

        canvas = Image.new(
            'RGB', (self.block_dimention["width"], self.block_dimention["height"]*height), color)
        draw = ImageDraw.Draw(canvas)

        def horizontal_alignement(
            txt, font): return self.block_dimention["width"] // 2 - font.getsize(txt)[0] // 2

        text_heights = [self.fonts.get(l["font"],self.fonts["regular"]).getsize(l["content"])[1] for l in lines]

        for i, line in enumerate(lines):
            # TODO: For now, align is not used. FIX IT later.
            draw.text(
                (
                    horizontal_alignement(
                        line["content"],
                        self.fonts.get(line["font"])
                    ),
                    # horizontal_alignement :) 
                    (self.block_dimention["height"] * \
                     height - sum(text_heights)) // 2 + 25 * i
                ),
                line["content"],
                font=self.fonts.get(line["font"]),
                fill=(0, 0, 0)
            )

        draw.line([(0,0), (self.block_dimention["width"],0)], fill ="black", width = 1)
        draw.line([(0,self.block_dimention["height"]*height), (self.block_dimention["width"],self.block_dimention["height"]*height)], fill ="black", width = 1)
        
     
        return canvas

    def generate_column(self, blocks: list[Image.Image], block_posistion_in_grid: list[int]) -> Image.Image:
        """Generate a column of the timetable with given blocks as an image.

        Args:
            blocks (list): The blocks of the column as images.
            block_posistion_in_grid (list[int]): Position of the blocks in the grid.

        Returns:
            Image.Image: Generated column.
        """        
        canvas = Image.new(
            'RGB', (self.block_dimention["width"], self.block_dimention["height"]*self.timetable_dimention["height"]), color='white')
        draw = ImageDraw.Draw(canvas)

        for i, block in enumerate(blocks):
            canvas.paste(
                block, (0, block_posistion_in_grid[i]*self.block_dimention["height"]))

        draw.line([(0,0), (0,self.timetable_dimention["height"] * self.block_dimention["height"])], fill ="black", width = 1)
        draw.line([(self.block_dimention["width"],0), (self.block_dimention["width"],self.timetable_dimention["height"] * self.block_dimention["height"] )], fill ="black", width = 1)
        return canvas

    def generate_timetable(self, columns: list[Image.Image]) -> Image.Image:
        """Generate a timetable image.

        Args:
            columns (list[Image.Image]): The columns of the timetable as images.

        Returns:
            Image.Image: Return the generated timetable.
        """        
        ruler_dimention = {
            "width": 50,
            "height": self.block_dimention["height"]*self.timetable_dimention["height"]
        }

        canvas = Image.new('RGB', (self.block_dimention["width"]*self.timetable_dimention["width"] + ruler_dimention["width"],
                           self.block_dimention["height"]*self.timetable_dimention["height"]), color='white')
        draw = ImageDraw.Draw(canvas)

        # Draw the ruler at left

        s,f = self.time_range
        for i in range(s,f+1):
            x_position = 0
            y_position = self.block_dimention["height"] * (i - self.time_range[0])
            draw.text((x_position, y_position),
                      f'{i}h', font=self.fonts["bold"], fill=(0, 0, 0))
            draw.line([(0,(i -s)  * self.block_dimention["height"] ),(ruler_dimention["width"],(i -s) * self.block_dimention["height"])], fill ="black", width = 1)

        # Past columns

        for i, column in enumerate(columns):
            canvas.paste(
                column,
                (ruler_dimention["width"] + self.block_dimention["width"]*i, 0)
            )

        return canvas
