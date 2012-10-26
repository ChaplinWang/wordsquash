#!/usr/bin/perl -w

sub markup_to_HTML($) {
	my ($text) = @_;
	$text =~ s/\[(\/?[bius])\]/<$1>/gi;
	
	$text =~ s/\[url\]([^\[]*)\[\/url\]/<a href='$1'>$1<\/a>/gi;
	$text =~ s/\[img\]([^\[]*)\[\/img\]/<img src='$1'alt="" \/>/gi;	
	$text =~ s/\[quote\]([^\[]*)\[\/quote\]/<blockquote><p>$1<\/p><\/blockquote>/gi;
	$text =~ s/\[code\]([^\[]*)\[\/code\]/<pre>$1<\/pre>/gi;		
	
	
	$text =~ s/\[(\/?(table|tr|td))\]/<$1>/gi;
	$text =~ s/\[size=(\d+)\]([^\[]*)\[\/size\]/<span style="font-size:$1px">$2<\/span>/gi; 


	$text =~ s/\[color=#?(\w{2}\d{4})\]([^\[]*)\[\/color\]/<span style="color:#$1">$2<\/span><font color="#$1">$2<\/font>/gi;
	if ($text =~ /\[color=(\w+)\]([^\[]*)\[\/color\]/i){
		$a = "FF0000";
		$text =~ s/\[color=(\w+)\]([^\[]*)\[\/color\]/<span style="color:#$a">$2<\/span><font color="#$a">$2<\/font>/gi;
	}                                    #To-do this is just red color not yet implement the others, need a table of hex then implement them.

	$text =~ s/\[\*]([^\[]*)/<li>$1<\/li>/gi; 
	$text =~ s/\[\/list\]/<\/ul>/gi;
	$text =~ s/\[list\]/<ul>/gi;  
											  #To_do faces 
											  #To_do Users should not be permitted to directly enter HTML. 


	#print"\n$1??\n$2!!\n";

	return $text;
}


while(<STDIN>){
	print markup_to_HTML($_);
}



