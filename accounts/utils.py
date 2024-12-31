from PIL import Image, ImageDraw
import os

def create_default_profile_image():
    # إنشاء صورة 400×400 بخلفية رمادية فاتحة
    img = Image.new('RGB', (400, 400), '#f0f2f5')
    draw = ImageDraw.Draw(img)
    
    # رسم دائرة داكنة للأفاتار
    draw.ellipse([100, 100, 300, 300], fill='#dfe3ee')
    
    # رسم أيقونة شخص بسيطة
    draw.ellipse([175, 150, 225, 200], fill='#90949c')  # الرأس
    draw.rectangle([160, 210, 240, 300], fill='#90949c')  # الجسم
    
    # التأكد من وجود المجلد
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'default')
    os.makedirs(output_dir, exist_ok=True)
    
    # حفظ الصورة
    output_path = os.path.join(output_dir, 'default_avatar.png')
    img.save(output_path)
    return 'default/default_avatar.png'

if __name__ == '__main__':
    create_default_profile_image()
