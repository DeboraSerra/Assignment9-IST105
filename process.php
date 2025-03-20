<?php
  $origin = $_GET['origin'];
  $dest = $_GET['dest'];

  $command = escapeshellcmd("python3 openroute_directions.py $origin $dest");
  $output = shell_exec($command);
  // display ip address of server or the host if an error occurs
  $host = gethostname();
  $host = gethostbyname($host);
  
  echo '<div style="max-width: 500px; margin: 128px auto 0; padding: 16px; border: 1px solid #999; border-radius: 4px;">';
  echo "<h1 style='text-align: center; margin: 32px 0;'>HOST IP: $host</h1>";
  echo "<hr>";
  echo $output;
  echo '</div>';
?>