from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import requests
from io import BytesIO
import os

class ImageComposer:
    """Utility for composing quote images."""
    
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height
    
    def load_image_from_url(self, url):
        """Download and load image from URL."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert('RGB')
        except Exception as e:
            raise ValueError(f"Failed to load image from URL: {str(e)}")
    
    def load_image_from_file(self, filepath):
        """Load image from local file."""
        try:
            return Image.open(filepath).convert('RGB')
        except Exception as e:
            raise ValueError(f"Failed to load image from file: {str(e)}")
    
    def resize_and_crop(self, img, width=None, height=None):
        """Resize and crop image to fit canvas."""
        if width is None:
            width = self.width
        if height is None:
            height = self.height
        
        # Calculate aspect ratio
        img_aspect = img.width / img.height
        target_aspect = width / height
        
        if img_aspect > target_aspect:
            # Image is wider, crop sides
            new_width = int(img.height * target_aspect)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        else:
            # Image is taller, crop top/bottom
            new_height = int(img.width / target_aspect)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, img.width, top + new_height))
        
        return img.resize((width, height), Image.Resampling.LANCZOS)
    
    def apply_overlay(self, img, opacity=0.4, color='black'):
        """Apply dark overlay to make text more readable."""
        overlay = Image.new('RGBA', img.size, (0, 0, 0, int(255 * opacity)))
        img_rgba = img.convert('RGBA')
        img = Image.alpha_composite(img_rgba, overlay).convert('RGB')
        return img
    
    def get_best_font_size(self, text, font_path, max_width, max_height):
        """Find best font size for text to fit in area."""
        font_size = 48
        while font_size > 8:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()
            
            bbox = Image.new('RGB', (1, 1))
            draw = ImageDraw.Draw(bbox)
            
            text_bbox = draw.multiline_textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            if text_width <= max_width and text_height <= max_height:
                return font_size, font
            
            font_size -= 2
        
        return 8, ImageFont.load_default()
    
    def compose(self, background_image, quote_text, author=None, 
                text_color='white', use_overlay=True, overlay_opacity=0.3):
        """Compose image with quote overlay.
        
        Args:
            background_image: PIL Image or URL string
            quote_text: Quote text to overlay
            author: Author name (optional)
            text_color: Color for text (hex or name)
            use_overlay: Whether to apply dark overlay
            overlay_opacity: Opacity of overlay (0-1)
        
        Returns:
            PIL Image (RGB)
        """
        # Load background if it's a URL
        if isinstance(background_image, str):
            img = self.load_image_from_url(background_image)
        else:
            img = background_image
        
        # Resize and crop to canvas
        img = self.resize_and_crop(img, self.width, self.height)
        
        # Apply overlay if requested
        if use_overlay:
            img = self.apply_overlay(img, opacity=overlay_opacity)
        
        # Prepare text
        if author:
            full_text = f'"{quote_text}"\n\n— {author}'
        else:
            full_text = f'"{quote_text}"'
        
        # Find best font size
        font_size, font = self.get_best_font_size(
            full_text, 
            'arial.ttf' if os.path.exists('arial.ttf') else 'DejaVuSans.ttf',
            self.width - 100,
            self.height - 200
        )
        
        # Draw text
        draw = ImageDraw.Draw(img)
        text_bbox = draw.multiline_textbbox((0, 0), full_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        
        draw.multiline_text(
            (x, y),
            full_text,
            fill=text_color,
            font=font,
            align='center',
            spacing=10
        )
        
        return img
    
    def save_to_bytes(self, img, format='PNG', quality=95):
        """Save image to bytes buffer."""
        buf = BytesIO()
        if format == 'JPEG':
            img.save(buf, format=format, quality=quality)
        else:
            img.save(buf, format=format)
        buf.seek(0)
        return buf
