case $1 in
[0-9] )
	echo "Its a number"; exit; ;;
[a-z] )
	echo "Its a letter"; 
	;;
esac
# comment on its own line
function fun() {
echo hi # comment after command
}

if [ 1 == 0 ]; then echo hi; fi

if [ 1 == 0 ]
then
echo hi
fi

fun
