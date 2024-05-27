const express = require("express");
const pool = require("../database");
const router = express.Router();

router.get("/webhook", (req, res) => {
  res.send("hola");
});

router.post("/webhook", async (req, res) => {
  // console.log(req.body.queryResult.queryText);//1000889
  // console.log(req.body.queryResult.parameters);//{ tipoMaterial: '1000889' }
  // console.log(req.body.queryResult.intent.displayName);//intent
  // console.log('**********');

  // console.log(req.body.queryResult.outputContexts);

  // [
  //   {
  //     name: 'projects/abastbot-ptca/agent/sessions/7a4066b5-3e8d-f67d-ce2a-b904b46eac2d/contexts/__system_counters__',
  //     parameters: {
  //       'no-input': 0,
  //       'no-match': 0,
  //       tipoMaterial: '1000889',
  //       'tipoMaterial.original': '1000889'
  //     }
  //   }
  // ]
  let valor = "";

  if(req.body.queryResult.intent.displayName == 'Situacion'){
    let material = req.body.queryResult.parameters.tipoMaterial;
    try {
      const rows = await pool.query("SELECT Almacen, LibreUtil FROM status WHERE Material = ? ",[material]);
      for (var i = 0; i < rows.length; i++) {
        valor = valor +" "+rows[i].Almacen.toString()+":"+rows[i].LibreUtil.toString();
      }      
      //valor = rows[0].LibreUtil.toString();
      console.log('***************************');
      console.log(rows[0].LibreUtil.toString());
    } catch (error) {
      console.log(error);
    }
    
  }

  if(req.body.queryResult.intent.displayName == 'pendientes'){
    let material = req.body.queryResult.parameters.tipoMaterial;
    try {
      const rows = await pool.query("SELECT Pedidos FROM status WHERE Material = ? limit 1",[material]);
      valor = rows[0].Pedidos.toString();
      console.log(rows[0]);
    } catch (error) {
      console.log(error);
    }    
    
  }

  const responseData = {
    fulfillmentMessages: [
      {
        text: {
          text: [valor],
        },
      },
    ],
  };

  const jsonContent = JSON.stringify(responseData);
  res.end(jsonContent);
});

module.exports = router;
