<!DOCTYPE html>
<html lang="sv">
<head>
  <title>Statistik Arbetstid | Micke Kring</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-+0n0xVW2eSR5OomGNYDnhzAbDsOXxcvSN1TPprVMTNDbiYZCxYbOOl7+AMvyTG2x" crossorigin="anonymous">
  <link rel="stylesheet" type="text/css" href="style.css">
  <link href="https://fonts.googleapis.com/css?family=Poppins:300,400,700,900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.3.1/css/all.css" integrity="sha384-mzrmE5qonljUremFsqc01SB46JvROS7bZs3IO2EmfFsd15uHvIt+Y8vEf7N7fWAU" crossorigin="anonymous">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.0/jquery.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.1/dist/js/bootstrap.bundle.min.js" integrity="sha384-gtEjrD/SeCtmISkJkNUaaKMoLD0//ElJ19smozuHV6z3Iehds+3Ulb9Bn9Plx0x4" crossorigin="anonymous"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  
  <script>
  $(document).ready(function() {
      $(".divtime").load("time.php");
      var refreshId = setInterval(function() {
      $(".divtime").load("time.php");
      }, 5000);
      $(".divstatus").load("status.php");
      var refreshId2 = setInterval(function() {
      $(".divstatus").load("status.php");
      }, 5000);
      $(".7weekcats").load("7weekcats.php");
      var refreshId3 = setInterval(function() {
      $(".7weekcats").load("7weekcats.php");
      }, 5000);
      $(".7weekhours").load("7weekhours.php");
      var refreshId4 = setInterval(function() {
      $(".7weekhours").load("7weekhours.php");
      }, 5000);
  });
  </script>

</head>

<body>

<div class="container-fluid">
    
   <div class="row">
    
      <div class="col-md-4">
      
        <div class="row">
        <div class="div1-half-top">
        <h2 class="calheading">STATISTIK | ARBETSTID</h2>
        <div class="divtime"></div></div></div>
        
        <div class="row">
        <div class="div1-half-top">
        <h2 class="calheading">TOTALT LÄSÅRET 21/22</h2>
        <div class="divstatus"></div></div></div>
     
      </div>
    
      <div class="col-md-8">
        
        <div class="row">
        <div class="div1-half-top">
        <h2 class="calheading">SENASTE 7 VECKORNA - ARBETSUPPGIFTER (%)</h2>
        <div>
        <canvas id="myChart30"></canvas>
        <div class="7weekcats"></div>
        </div>
        </div>
        </div>
        
        <div class="row">
        <div class="div1-half-top">
        <h2 class="calheading">SENASTE 7 VECKORNA - ARBETAD TID (TIM)</h2>
        <div>
        <canvas id="myChart1"></canvas>
        <div class="7weekhours"></div>
        </div>
        </div>
        </div>
   
      </div>

  </div>


</div>

</body>
</html>