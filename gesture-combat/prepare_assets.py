import pygame

def process_sprite(src_path, dst_path, target_size, black_thresh=25):
    img = pygame.image.load(src_path)
    w, h = img.get_size()
    
    # Scale down smoothly first
    scaled = pygame.transform.smoothscale(img, target_size)
    sw, sh = scaled.get_size()
    
    # Create surface with alpha
    out = pygame.Surface((sw, sh), pygame.SRCALPHA)
    
    # Process transparency
    for x in range(sw):
        for y in range(sh):
            r, g, b, _ = scaled.get_at((x, y))
            if r < black_thresh and g < black_thresh and b < black_thresh:
                out.set_at((x, y), (0, 0, 0, 0)) # Fully transparent
            else:
                out.set_at((x, y), (r, g, b, 255))
                
    pygame.image.save(out, dst_path)
    print(f"Saved {dst_path} ({sw}x{sh})")

def process_floor(src_path, dst_path, target_size=(128, 128)):
    img = pygame.image.load(src_path)
    scaled = pygame.transform.smoothscale(img, target_size)
    pygame.image.save(scaled, dst_path)
    print(f"Saved {dst_path} ({target_size[0]}x{target_size[1]})")

if __name__ == '__main__':
    pygame.init()
    # Mock video mode for safe surface handling
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    process_sprite('assets/player.jpg', 'assets/player.png', (72, 72), black_thresh=28)
    process_sprite('assets/golem.jpg', 'assets/golem.png', (96, 96), black_thresh=28)
    process_sprite('assets/stalker.jpg', 'assets/stalker.png', (80, 80), black_thresh=28)
    process_floor('assets/floor.jpg', 'assets/floor.png', (128, 128))
    print("All game sprites processed successfully!")
