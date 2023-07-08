<?php
    define('SERVICE', '2');
    include(dirname(__FILE__) . '/../config.php');
    
    $db = new SQLite3("");

    $tables = 'CREATE TABLE heap (ptr INTEGER PRIMARY KEY, data VARCHAR(60))';
    $db->query($tables);

    $head = 0;
    $notes = [];


    function malloc($text){
        global $head;
        global $db;

        if(strlen($text) > 60){
            return;
        }
        $head ++;

        $query = "INSERT INTO heap VALUES ($head, '$text')";
        $db->query($query);
    }

    function free($ptr){
        global $head;
        global $db;

        $query = "DELETE FROM heap WHERE ptr = $ptr;";
        $db->query($query);

        if($ptr == $head){
            $head--;
        }
    }

    function read($ptr){
        global $db;
        $query = "SELECT data FROM heap WHERE ptr = $ptr";
        $res = $db->query($query);

        $data =  $res->fetchArray();
       
        return $data['data'];
    }

    function realloc($ptr, $text){
       global $db;
       free($ptr);
       $query = "INSERT INTO heap VALUES ($ptr, '$text')";
       $res = $db->query($query);
    }

    function menu(){

        echo "---- WELCOME TO NOTEKEEP, the house of SQL ----\n";
        echo "Menu:\n";
        echo "1) Add note\n";
        echo "2) Read a note\n";
        echo "3) Delete a note\n";
        echo "4) Guess the note!";
        echo "5) Exit\n";

        return (int) readline_p(">");
    }
    

    function create_a_note(){
        echo "Enter your text, a max of 60 characters is allowed.\n";
        $text = readline_p('>');
        global $head;

        if(strlen($text) > 60){
            echo "Not allowed.\n";
            return FALSE;
        }
        global $notes;

        if(count($notes) >= 3){
            $ptr = array_shift($notes);
            array_push($notes, $ptr);
            realloc($ptr, $text);
        }else{
            malloc($text);
        }
        if(array_search($head, $notes) === FALSE){
            array_push($notes, $head);
        }
    }

    function delete_a_note(){
        global $head;
        global $notes;
        print_notes();
        $ptr = (int) readline_p('>');

        if(array_search($ptr, $notes) === FALSE) return;
        free($ptr);

        unset($notes[array_search($ptr, $notes)]);

    }

    function read_a_note(){
        print_notes();

        global $notes;
        global $debug;
        $ptr = (int) readline_p('>');
        
        if(!$debug && array_search($ptr, $notes) === FALSE){
            echo 'This is not a note!' . "\n";
            return FALSE;
        }
        $text = read($ptr);
        echo "\n$text\n";
    }
    
    function print_notes(){
        global $notes;
        echo 'Your notes: [';

        echo implode(',', $notes);
        echo "]\n";
    }

    function test(){
        $id = (int) readline_p("id:\n>");
        $hash = readline_p('md5($data): ');
        $data = read($id);
        if($hash == md5($data)){
            echo $data . "\n";
        }else{
            echo "Wrong guess\n";
        }
    }

# insert flag in db
$debug = trim(readline_p("Debug? (y/n)\n>"));

if($debug == 'y'){
    $flag = readline_p("Enter test flag: ");
    malloc($flag);
    $debug = TRUE;
}else{
    $debug = FALSE;
    malloc(FLAG);
}


while(True){
    global $head;
    global $notes;
    global $debug;
    if($debug){
        var_dump($head) . "\n";
    }
    $choice = menu();
    switch($choice){
        case 2:
            read_a_note();
            break;
        case 3: 
            delete_a_note();
            break;
        case 5:
            echo "bye bye";
            die();
        case 1:
            create_a_note();
            break;
        case 4:
            test();
            break;
        default:
            break;
        }

}
