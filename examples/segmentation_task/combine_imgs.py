from PIL import Image

def combine_images(directory, out_directory, view, f1, f2, f3 ):


    for idx, value in enumerate(range(0, 867)):
        image_paths=[
            f"D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\animation\\original/{view}/frame_{idx:04d}.png",
            f"{directory}/{f1}/{view}/frame_{idx:04d}.png",
            f"{directory}/{f2}/{view}/frame_{idx:04d}.png",
            f"{directory}/{f3}/{view}/frame_{idx:04d}.png"
        ]
        
        images = [Image.open(path) for path in image_paths]
        
        # Ensure all images have the same size
        widths, heights = zip(*(img.size for img in images))
        if len(set(widths)) > 1 or len(set(heights)) > 1:
            raise ValueError("All images must have the same dimensions")
        
        # Combine images horizontally
        total_width = sum(widths)
        max_height = max(heights)
        combined_image = Image.new("RGB", (total_width, max_height))
        
        # Paste images side-by-side
        x_offset = 0
        for img in images:
            combined_image.paste(img, (x_offset, 0))
            x_offset += img.size[0]
        
        # Save the result
        out_path = f"{out_directory}/{view}/frame_{idx:04d}.png"
        combined_image.save(out_path)

        print(f"Combined image saved at {out_path}")

# Example usage:
if __name__ == "__main__":
    # Directory containing point clouds
    directory = "D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\animation\\diff"
    out_directory = "D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\animation\\\\diff\\combined_5"
    
    # Call the function to display and save point clouds
    combine_images(directory,out_directory, 'back', 'filtered_5', 'filtered_5_n2', 'filtered_5_n3')
    combine_images(directory,out_directory, 'front','filtered_5', 'filtered_5_n2', 'filtered_5_n3')
    combine_images(directory,out_directory, 'perspective','filtered_5', 'filtered_5_n2', 'filtered_5_n3')
    combine_images(directory,out_directory, 'side', 'filtered_5', 'filtered_5_n2', 'filtered_5_n3')