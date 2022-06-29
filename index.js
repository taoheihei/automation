const express = require("express") ;
const fs = require("fs");
const bodyParser= require("body-parser");
const app = express()
const port = 3000
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: false}));

app.post('/verifycode', (req, res) => {
  const code = req.body.code;
  console.log(code);
  try{
  fs.appendFileSync('phoneCode.txt',"\n"+ code);
  } catch(e){
    console.error(e);
    res.send({success: false});
    return;
  }
  res.send({success: true});
})



app.listen(port, () => {
  console.log(`app listening on port ${port}`)
})