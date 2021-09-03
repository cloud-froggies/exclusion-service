'use strict';

const express = require('express');
const { query,validationResult } = require('express-validator');

var mysql = require('mysql2/promise');



// Constants
const PORT = 8080;
const HOST = '0.0.0.0';

// App
const app = express();
app.get('/', (req, res) => {
  res.send({'Service':'exclusions'});
});


app.get('/exclusion',
[
  query('publisher').isInt().withMessage('debe enviar un publisher id como parametro'),
  query('advertiser_campaigns').split(',').isArray({min:1}).withMessage('debe haber al menos 1 campaña en el parametro advertiser_campaigns')
],
async (req,res)=>{

  const errors = validationResult(req);

  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  console.log(process.env.db_endpoint)
  console.log(process.env.db_admin_user)
  console.log(process.env.db_admin_password)
  console.log(process.env.db_name)

  var publisher = req.query.publisher
  var advertiser_campaigns = req.query.advertiser_campaigns
  
  var connection 
  if (typeof connection === 'undefined') {
    try {
        connection = await mysql.createConnection({
            host: process.env.db_endpoint,
            user: process.env.db_admin_user,
            password: process.env.db_admin_password,
            database: process.env.db_name
        });    
    }
    catch(err) {
        console.log(err);
        throw new Error('Database connection error');
    }
  }
  var rows
  var fields
  try {
      [rows, fields] = await connection.query(`SELECT c.id
      FROM publisher_exclusions e
      JOIN advertisers a ON e.advertiser_id = a.id
      JOIN advertiser_campaigns c ON a.id = c.advertiser_id
      WHERE e.publisher_id = ?
      AND c.id IN ?`,[publisher, advertiser_campaigns]);
  }
  catch(err) {
      console.log(err)
      throw new Error('Database query error');
  }
  if (rows.length > 0)
      return rows;
  else
      throw new Error('No data');

});

app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);

