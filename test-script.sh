case $1 in
[0-9] )
	echo "It's a number"; exit; ;;
[a-z] )
	echo "Its a letter"; 
	;;
esac
# comment on its own line
function fun() {
echo hi # comment after command
}

if [ "1" == "0" ]; then echo hi; fi

if [ "1" == "0" ]
then
echo hi
elif [ "2" == "9" ]; then
echo blah
else
	echo hi
fi
x='
   x is a multi
line
\tquote
'
fun
