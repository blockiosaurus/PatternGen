import os

for file in os.listdir('./json'):
    with open('./json/' + file, 'r') as read_file:
        contents = read_file.read()
        if 'https://breadheads.s3.amazonaws.com/babybreads/eyes/mint' not in contents:
            #print(contents)
            print("Fixing " + file)
            new_contents = contents.replace('"image": "', '"image": "https://breadheads.s3.amazonaws.com/babybreads/eyes/mint/')
            new_contents = new_contents.replace('"uri": "', '"uri": "https://breadheads.s3.amazonaws.com/babybreads/eyes/mint/')
            with open('./json/' + file, 'w') as write_file:
                write_file.write(new_contents)
                #print(new_contents)
                write_file.close()
                #quit()