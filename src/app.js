var https = require('https');
var fs = require('fs');
const express = require("express");

var httpsOptions = {
    key: fs.readFileSync('client-key.pem'),
    cert: fs.readFileSync('client-cert.crt')
};

const app = express();

app.use(express.static('static'));

app.get('/', (req,res)=>{
    res.statusCode = 200;
    res.writeHead(200, { 'content-type': 'text/html' });
    fs.createReadStream('index.html').pipe(res);
});

https.createServer(httpsOptions, app).listen(4433);
