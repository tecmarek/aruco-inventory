# aruco-inventory
Simple proof of concept for using aruco markers to quickly find an inventory position based on its marker ID.
Runs locally in the devices browser. Therefor the performance varies drastically based on the used device!


# Generating needed ssl key pair
Run the following command in the src folder:

    openssl req -newkey rsa:2048 -nodes -keyout client-key.pem -x509 -days 3650 -out client-cert.crt

This is a self signed certificate which your browser does not accept by default. You can either add it to your browser or simply accept the warning your browser is giving you.

# Running the server
In the src folder to install run:

    npm install

and to start the server

    npm run start

you can then open the server locally under https://127.0.0.1:4433/ or open it in your network replacing 127.0.0.1 with your PCs IP address.

# Application in use

Printed tags 10mm x 10mm in size (option showing all outlines enabled):

![Example 10x10mm](docs/example_10x10mm.jpg)


Printed tags 20x20mm in size (options showing all outlines and IDs enabled):

![Example 20x20mm](docs/example_20x20mm.jpg)

Printed tags 5mm x 5mm in size (option showing all outlines enabled):

![Example 5x5mm](docs/example_5x5mm.jpg)

Printed tags 5mm x 5mm in size:

![Example 5x5mm](docs/example_5x5mm_only_highlight.jpg)