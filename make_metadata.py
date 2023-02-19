for num in range(0, 10000):
    with open("metadata_template.json", "r") as f:
        metadata = f.read()
        metadata = metadata.replace("#000", "| #" + str(num + 1))
        metadata = metadata.replace("image.png", str(num) + ".png")
        with open("json/" + str(num) + ".json", "w") as out:
            out.write(metadata)