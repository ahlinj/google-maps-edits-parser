# Google Maps Edits Parser

This Python script converts your contributions (edits) stored in JSONs to a KML file(s).

## How to use it?

1. Go to **[Google Takeout](https://takeout.google.com/settings/takeout)** and deselect everything apart from "Maps".

2. Click on the "All Maps data included" button in the Maps section and select "Instructions."

3. Follow Google's instructions, and after some time, you will receive the needed data on your Gmail account.

4. Download your data and unzip the folder.

5. Download this Python script and run it. You need Python on your computer to be able to run it. Another option is also to download the executable that I created for people who don't want to deal with Python scripts. You can find the executable **[here](https://github.com/ahlinj/google-maps-edits-parser/releases/tag/v2.1)**.

6. Once you run the script or the executable select the Instructions folder and wait for the program to finish.

7. When it's finished, you will have your coordinates.kml file in the Instructions folder. If you had more than 2000 contributions, you would also find coordinates_chunk_i.kml files.

8. You can view your edits by opening the coordinates.kml file with Google Earth Pro or importing them in Google My Maps. Google My Maps has a limit of 2000 points per file, so you will have to individually import each chunk into your map. Another limit is that each layer can only have 10000 points, meaning you would have to create multiple layers and upload 5 chunks in each layer.

## Statistics

    Disclaimers: 
        1. This feature is only supported using the python script directly and is not packaged in the executable.
        2. You will need to install reverse_geocoder library
        3. The statistics may not be 100% accurate

    A stats.txt file will be generated, showing number of edits in particular country, 1st and 2nd administrative division.