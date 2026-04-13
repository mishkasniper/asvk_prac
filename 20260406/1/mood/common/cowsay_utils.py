from io import StringIO
from cowsay import read_dot_cow

jgsbat = read_dot_cow(StringIO("""
$the_cow = <<EOC;
         $thoughts
          $thoughts
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\\\\\\\--//|.'-._  (
     )'   .'\/o\/o\/'.   `(
      ) .' . \====/ . '. (
       )  / <<    >> \  (
        '-._/``  ``\_.-'
  jgs     __\\\\\\\\'--'//__
         (((""`  `"")))
EOC
"""))