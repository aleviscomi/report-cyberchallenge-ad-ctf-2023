<?php


  $token = readline_p("Enter your token: ");

  $dbhost = getenv('DBHOST');
  $dbschema = getenv('DBSCHEMA');

  $dbusername = 'root';
  $dbpass = getenv('DBPASS');

  $conn = new mysqli($dbhost, $dbusername, $dbpass, $dbschema);

  $query = 'SELECT flag FROM service WHERE id = ? AND service = ' . SERVICE ;

  $stm = $conn->prepare($query);

  $stm->bind_param('s', $token);
  $stm->execute();
  $result = $stm->get_result();
  $flag = $result->fetch_assoc();

  if(!$flag){
      die('Invalid Token');
  }
  define('FLAG', $flag['flag']);

  function print_flag(){
      global $conn;
      echo FLAG;

      $query = 'DELETE FROM service WHERE id = ? and service = ' . SERVICE;
      $stm = $conn->prepare($query);
      $stm->bind_param('s', $token);
      $stm->execute();
  }
/* Fixes PHP's buffering. For whatever reason PHP does not call flush after readline */
function readline_p($prompt){
    echo $prompt;
    return readline();
}

function insert_seeds($seeds){

    global $token;
    global $conn;

    foreach($seeds as $seed){
        $query = "INSERT INTO eightbitroulette_seeds (token, seed) VALUES (?, ?)";
        $stm = $conn->prepare($query);
        $stm->bind_param("si", $token, $seed);
        $stm->execute();
    }

}
