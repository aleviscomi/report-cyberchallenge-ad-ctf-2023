<?php
  define('SERVICE', '1');
  include(dirname(__FILE__) . '/../config.php');

  $seed_array = array();
  for($i=0; $i<300; $i++) $seed_array[$i] = mt_rand();

  insert_seeds($seed_array);

  ## DO NOT TOUCH THIS IF YOU WANT SLA
  function roulette_extraction($seed) {
    $v0 = $seed & 0xFFFF;
    $v1 = $seed >> 16;
    $su = 0;
    $de = 0x9e37;
    $k0 = 0x7dc3;
    $k1 = 0x1296;
    $k2 = 0x3ec1;
    $k3 = 0x7642;
    for ($i=0; $i < 32; $i++) {
        $su += $de;
        $su &= 0xFFFF;
        $v0 += (($v1<<4) + $k0) ^ ($v1 + $su) ^ (($v1>>5) + $k1);
        $v0 &= 0xFFFF;
        $v1 += (($v0<<4) + $k2) ^ ($v0 + $su) ^ (($v0>>5) + $k3);
        $v1 &= 0xFFFF;
    }
    return $v1&0xFF;
  }

  $money = 10;
  $extractions = 0;

  echo "Cat roulette!\n";

  while($money !== 0 && $extractions < 300){
    $seed = $seed_array[$extractions];
    $extractions++;
    $choice = 0;

    if($money > 10000){
      echo "Congratz!\n";
      print_flag();
      echo "\n";
      die();
    }

    echo "Extraction " . $extractions . " is starting...";
    echo "\nWhat do you want to do?\n";
    echo "1. Play 'number'\n";
    echo "2. Play 'parity'\n";
    echo "3. Play 'high'\n";
    echo "4. See my gaming history (skip this extraction)\n";
    echo "5. Print the rules (skip this extraction)\n";
    echo "0. Exit\n";

    $choice = (int)readline_p("Gimme choice: ");
    readline_add_history($choice);

    $real_extraction = roulette_extraction($seed);

    if($choice === 1){
      echo "You chose to play 'number'!\n";
      $bet = (int)readline_p("Gimme bet: ");
      readline_add_history($bet);
      $number_bet = (int)readline_p("On which number? ");
      readline_add_history($number_bet);
      if((int)log($number_bet, 2) >= 8 || !is_int($number_bet)) echo "Invalid number to bet on\n";
      else{
        $money -= $bet;
        if($number_bet === $real_extraction){
          $win = 255*$bet;
          $win = min(4095, $win);
          echo "You won " . $win . "!\n";
          $money += $bet + $win;
          readline_add_history(0);
        }
        else{
          echo "Sorry, you lost!\n";
          readline_add_history(1);
        }
      }
    }
    else if($choice === 2){
      echo "You chose to play 'parity'!\n";
      $bet = (int)readline_p("Gimme bet: ");
      readline_add_history($bet);
      $number_bet = readline_p("On odd or even? ");
      if($number_bet == 'odd'){
        readline_add_history(1);
        $money -= $bet;
        if($real_extraction%2 == 1){
          $win = (int)(1.5*$bet);
          $win = min(4095, $win);
          echo "You won " . $win . "!\n";
          $money += $bet + $win;
          readline_add_history(0);
        }
        else{
          echo "Sorry, you lost!\n";
          readline_add_history(1);
        }
      }
      else if($number_bet == 'even'){
        readline_add_history(0);
        $money -= $bet;
        if($real_extraction%2 == 0){
          $win = (int)(1.5*$bet);
          $win = min(4095, $win);
          echo "You won " . $win . "!\n";
          $money += $bet + $win;
          readline_add_history(0);
        }
        else{
          echo "Sorry, you lost!\n";
          readline_add_history(1);
        }
      }
      else echo "Invalid bet.\n";
    }
    else if($choice === 3){
      echo "You chose to play 'high'!\n";
      $bet = (int)readline_p("Gimme bet: ");
      readline_add_history($bet);
      $number_bet = (int)readline_p("On which number? ");
      readline_add_history($number_bet);
      if((int)log($number_bet, 2) >= 8 || !is_int($number_bet)) echo "Invalid number to bet on\n";
      else{
        $money -= $bet;
        if($number_bet <= $real_extraction){
          $win = (int)(256/(256-$number_bet)) - 1;
          $win = min(4095, $win);
          echo "You won " . $win . "!\n";
          $money += $bet + $win;
          readline_add_history(0);
        }
        else{
          echo "Sorry, you lost!\n";
          readline_add_history(1);
        }
      }
    }
    else if($choice === 4){
      readline_add_history(0);
      readline_add_history(0);
      readline_add_history(0);
      for($i = 0; $i<sizeof(readline_list_history()); $i += 4){
        $current_bet = array(readline_list_history()[$i], readline_list_history()[$i+1], readline_list_history()[$i+2], readline_list_history()[$i+3]);
        switch($current_bet[0]){
          case 1:
            echo "On extraction ". (int)($i/4+1) . " you played 'number', bet " . $current_bet[1] . " on the number " . $current_bet[2] . " and ";
            if($current_bet[3] == 0) echo "won.\n";
            else echo "lost.\n";
            break;
          case 2:
            echo "On extraction ". (int)($i/4+1) . " you played 'parity', bet " . $current_bet[1] . " on ";
            if($current_bet[2] == 1) echo "odd and ";
            else echo "even and ";
            if($current_bet[3] == 0) echo "won.\n";
            else echo "lost.\n";
            break;
          case 3:
            echo "On extraction ". (int)($i/4+1) . " you played 'high', bet " . $current_bet[1] . " on the number " . $current_bet[2] . " and ";
            if($current_bet[3] == 0) echo "won.\n";
            else echo "lost.\n";
            break;
          case 4:
            echo "On extraction ". (int)($i/4+1) . " you saw your gaming history.\n";
            break;
          case 5:
            echo "On extraction ". (int)($i/4+1) . " you saw the rules.\n";
            break;
        }
        if(array_reduce($current_bet, function($a, $b){return $a * $b;},1) == 1337) $extractions -= 1;
      }
    }
    ## DO NOT TOUCH THIS IF YOU WANT SLA - THE GAME SHOULD ALWAYS SATISFY THESE RULES
    else if($choice == 5){
      readline_add_history(0);
      readline_add_history(0);
      readline_add_history(0);
      echo "Rules for Cat roulette!\n";
      echo "1. You start with 10 coins, you must reach 10000 to win a flag. In the game there are 300 rounds.\n";
      echo "2. Maximum win for a single extraction is 4095 coins.\n";
      echo "3. For transparency, after every extraction you will be able to see the extraction seed.\n";
      echo "4. For transparency, the extraction algorithm is public and will never change:
      function roulette_extraction(seed) {
        v0 = seed & 0xFFFF;
        v1 = seed >> 16;
        su = 0;
        de = 0x9e37;
        k0 = 0x7dc3;
        k1 = 0x1296;
        k2 = 0x3ec1;
        k3 = 0x7642;
        for (i=0; i < 32; i++) {
            su += de;
            su &= 0xFFFF;
            v0 += ((v1<<4) + k0) ^ (v1 + su) ^ ((v1>>5) + k1);
            v0 &= 0xFFFF;
            v1 += ((v0<<4) + k2) ^ (v0 + su) ^ ((v0>>5) + k3);
            v1 &= 0xFFFF;
        }
        return v1&0xFF;
      }\n";
      echo "5. There are 3 different type of games: number, parity, high.\n";
      echo "6. If you play 'numbers', you can bet on a number and win int(min(4095, 255*bet)).\n";
      echo "7. If you play 'parity', you can bet if the extraction will be odd or even. You will win int(min(4095, 1.5*bet)).\n";
      echo "8. If you play 'high', you can bet that the extraction is higher than some number x chosen by you. You will win int(min(4095, 256/(256-x)-1)).\n";
      echo "Press enter to continue...\n";
      readline_p("");

    }
    else die();
    echo "Remaining Money: " . $money . "\n";
    echo "The number extracted was " . $real_extraction . " and the extraction seed was " . $seed . "\n";
  }
  echo "Bye!\n"
?>
