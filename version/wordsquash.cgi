#!/usr/bin/perl -w

# written by cbwa548@cse.unsw.edu.au May 2011
# as COMP2041 assignment 2
#Chengbin Wang
#z3313137


use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use List::Util qw/max/;

sub action_list_blogs();
sub action_display_blog();
sub action_edit_commenting();
sub create_blog();
sub save_posting();
sub markup_to_HTML($);
sub get_html_template($);
sub read_file($);
sub write_file($$);
sub check_post_title_exists($);
                                                                            #title{color:orange;text-align:center;}
                                                                            #h1{color:orange;text-align:center;}
# This HTML could be in a template file but it assists debugging to have it output ASAP
print header,"<html><head><style type='text/css'>
body{background-color:#d0e4fe;}
h1{color:orange;text-align:center;}
h2{color:orange;text-align:center;}
form{font-family:'Times New Roman';color:green;text-align:center;font-size:20px;}
li{font-family:'Times New Roman';text-align:center;font-size:20px;}
pre{font-family:'Times New Roman';text-align:center;font-size:20px;}
p{font-family:'Times New Roman';text-align:center;font-size:20px;}
href{font-family:'Times New Roman';text-align:center;font-size:20px;}
<title>WordSquash</title></head></style><body>\n";

# Leave parameters in a HTML comment for debugging
print "<!-- ".join(",", map({"$_='".param($_)."'"} param()))."-->\n";

print join(",", map({"$_='".param($_)."'"} param())),"<p>";

my $action = param('action') || 'login';
my $blog = param('blog') || '';
my $post = param('post') || '';
my $postContent = param('postContent') || '';
my $user_name = param('username') || '';
my $user_PST = param('userPST')|| '';
$url = "http://cgi.cse.unsw.edu.au/~cbwa548/ass2/wordsquash.cgi";

$blog =~ s/[^a-zA-Z0-9\-]//g;
$data_dir = "./data";
mkdir $data_dir if !-d $data_dir;
mkdir "$data_dir/temp" if !-d "$data_dir/temp";

my %attributes = (
	URL => url(),
	BLOG_HOST_NAME => WordSquash,
	BLOG => $blog,
	POST_TITLE =>$post,
	POST_CONTENT =>$postContent,
	USER =>$user_name,
	USERPST => $user_PST,
	BLOG_TITLE => param(new_blog_title) || read_file("$data_dir/$user_PST.$blog.blog_title")
	
);

print get_html_template("$action.start.template");
&{"action_$action"}() if defined &{"action_$action"};
print get_html_template("$action.end.template");

if ($action !~ 'login' && $action !~ 'regist' && $action !~ 'login_result'&& $action !~ 'regist_result' && $action !~ 'retreve_password' && $action !~ 'confirmation'){
    print get_html_template("search.template");
}

print "</body></html>\n";
exit(0);

sub action_login() {
print"<a href='$url?blog=$blog&action=register'>Register</a>";
print"<p><a href='$url?action=retreve_password'>forgotten password</a>";
}

sub action_confirmation() {
	my $em = read_file("$data_dir/temp/$user_name.information_email");
	my $pw = read_file("$data_dir/temp/$user_name.information");	
	write_file("$data_dir/$user_name.information", $pw);
	write_file("$data_dir/$user_name.information_email", $em);	  	
	print "<h2>Congratulations!<p>your account has been actived now, log in to your account<h2>";
	print  "<p><a href='$url'>login</a>";
}

sub action_retreve_password() {

        my $TempName = param(username);
        $TempName =~ s/[^0-9A-Za-z_]//g;
        param('username',$TempName);                 #for safty reason get rid of all irellavent carractor
        $user_name = param('username') || '';
        
        $TempEM = param(email_address);
        $TempEM =~ s/[^0-9A-Za-z_.@]//g;
        param('email_address',$TempEM);              #for safty reason get rid of all irellavent carractor

	if (param('email_address') ne '' && param('username' ) ne ''){


		my $t = sprintf "$data_dir/$user_name.information_email";
		my $file = read_file($t);
			if (!defined $file){
				print "<p>no such user<p>";
			}elsif (param('email_address') == $file){
				$t =~ s/_email//;
				my $pw = read_file($t);
				`mailx -s "$pw" "$TempEM"`;   #send password to valid email
				
				print "<p>A letter has been send to your email check your password!";															
			}else{
				print "<p>Are u cheating me?<p>wrong email address<p>"
			}
	}
		print get_html_template("retreve_password.post.template");
		print  "<p><small><a href='$url'>relogin</a></small>";

}

sub action_register() {}




sub action_view_posting() {
			my $location = param('location');
			$attributes{POST_TITLE} = read_file("${location}_title");       
			$attributes{POST_CONTENT} = markup_to_HTML(read_file($location));
		
			$location =~ /(\d{12})\W+([^\W]*).*/;
			$attributes{TIME} = $1;
			$attributes{PEOPLE} = $2;		
			print get_html_template("view_posting.post.template");
}

sub action_search_result() {

    print"<h1>SEARCH RESULT</h1><p>";

    foreach my $temp (sort glob "$data_dir/*") {

        if ($temp !~ /.information/){

            my $t = param(search_text);

            my $k = markup_to_HTML(read_file($temp)); 
             
            if($k =~ /$t/ ){

               if($temp =~ /.post$/){
					$temp =~ /(\d{12})\W+([^\W]*).*/;
					my $time = $1;
					my $people = $2;
			
				    print"$k <p>-----posted by $people at $time<p>";
				    print"<a href='$url?action=view_posting&username=$user_name&user_PST=$people&location=$temp'>View this posting</a><br><br><hr>";                   
               }
               elsif($temp =~ /.post_title$/){
					$temp =~ /(\d{12})\W+([^\W]*).*/;

					my $time = $1;
					my $people = $2;
					$temp =~ s/_title//;			
				    print"$k <p>-----posted by $people at $time<p>";
				    print"<a href='$url?action=view_posting&username=$user_name&user_PST=$people&location=$temp'>View this posting Title</a><br><br><hr>";                   
               }
               elsif($temp =~ /.comment$/){
					$temp =~ /(\d{12})\W+([^\W]*).*/;
					my $time = $1;
					my $people = $2;
								
				    print"$k <p>-----posted by $people at $time<p><hr>";                  
               }
               elsif($temp =~ /.blog_title$/){
					$temp =~ /$data_dir\/([^.]*)\.*/;

					my $people = $1;
								
				    print"$k <p>-----blog Title by $people<p><hr>";                  
               }         
            }
        }
    }
}

sub action_login_result() {
     
        my $TempName = param(username);
        $TempName =~ s/[^0-9A-Za-z_]//g;
        param('username',$TempName);            #for safty reason get rid of all irellavent carractor
        $user_name = param('username') || '';
        
        $TempPW = param(password);
        $TempPW =~ s/[^0-9A-Za-z_]//g;
        param('password',$TempPW);              #for safty reason get rid of all irellavent carractor

       if (!check_password_correct(param(username))) {
	     print "<p><font color=\'red\'><b>(login failed)not valid name and password</b></font><p>";
	     print"<a href='$url?action=login'>Try again</a>";
         print"<p><a href='$url?action=retreve_password'>forgotten password</a>";
       }else{
         print "<p>login successful<p>";
         print"<input type='hidden' name='action' value='list_blogs'>";
         print"<input type='hidden' name='username' value= param(username)>";
         param('username',$user_name);

         print"<a href='$url?action=list_blogs&username=$user_name'>View Blogs</a>"; 
    }
}

sub action_regist_result() {
	if (param(username) ne '' && param(password) ne ''&& param(email) ne ''){  
	    save_regist();
	    print "<p>regist successful<p>";
	    my $EMaddress = param(email);
	    my $confermationLetter = "http://cgi.cse.unsw.edu.au/~cbwa548/ass2/wordsquash.cgi?action=confirmation&username=$user_name";   #send confirmation letter
	    `mailx -s "$confermationLetter" "$EMaddress"`;
	    print "<p><a href='$url?action=login'>Login</a><br>";
	}else{
	    print"<p><font color=\'red\'><b>(regist failed) missing or conflict clomloms plz Register again</b></font><p>";
	    print"<a href='$url?blog=$blog&action=register'>Register Again</a>"
	}
}


# List blogs
sub action_list_blogs() {

print"<p><br><br><b><font color=\'green\'>my blogs</b></font><br><ul>";
	foreach my $blog (sort glob " $data_dir/$user_name.*.blog_title") {
	
		($attributes{BLOG} = $blog) =~ s/\.blog_title$//;		       
		($attributes{BLOG} = $attributes{BLOG}) =~ s/$data_dir\/$user_name\.//;
		 $attributes{USERPST} = $user_name;	
		 $attributes{USER} = $user_name;
		            
		$attributes{BLOG_TITLE} = read_file("$blog");
		print get_html_template('list_blogs.blog.template');		
	}
	print "</ul><p><a href='$url?blog=$blog&action=new_blog&username=$user_name'>Create a new blog</a><br>";

    print"<br><br><b><font color=\'green\'>View others blogs</b></font><br><ul>";		
    foreach my $blog (sort glob "$data_dir/*.*.blog_title") {
       if ($blog !~ "$data_dir/$user_name.*.blog_title"){
        if ($blog =~ /\/data\/([^.]*).([^.]*).blog_title/){
              $user_PST = $1;
              $blog_name = $2;                  
        }        
		($attributes{BLOG} = $blog) =~ s/\.blog_title$//;		       
        ($attributes{BLOG} = $attributes{BLOG}) =~ s/$data_dir\/$user_PST\.//;
		$attributes{USER} = $user_name;
		$attributes{USERPST} = $user_PST;		            
		$attributes{BLOG_TITLE} = read_file("$blog");
		print get_html_template('list_blogs.blog.template');
       }
	} 

    print  "</ul><p><small><a href='$url'>Log off</a></small>";
	

}

# Display a blog's contents
sub action_display_blog() {

	create_blog() if (defined param(new_blog_title));
	save_posting() if defined param(new_posting_contents);
    save_edit_posting() if defined param(edit_posting_contents);
    delete_post() if defined param(delete_posting);    


	foreach my $post (sort glob "$data_dir/*.$user_PST.$blog.*.post") {

		$attributes{POST_TITLE} = read_file("${post}_title");       
		$attributes{POST_CONTENT} = markup_to_HTML(read_file($post));
		
	     		
		$post =~ /(\d{12})\W+([^\W]*).*/;
		$attributes{TIME} = $1;
		$attributes{PEOPLE} = $2;

        my $tempPostTitle = read_file("${post}_title");
           $tempPostTitle =~ s/\s+/_/g; 
	    my $last_comment = max(map(/(\d+).comment/, glob("$data_dir/*.$blog.$tempPostTitle.*.comment")));


		$attributes{N_COMMENTS} = ($last_comment || 0);
		
		$attributes{LOCATION} = $post;
		print get_html_template("display_blog.post.template");
		if($user_PST eq $user_name){
		    print get_html_template("print_posting_delete.template");
		    print get_html_template("print_posting_edit.template");
        }
	}
	print"<hr>";
	if($user_PST eq $user_name){
	 print "</ul><p><a href='$url?blog=$blog&action=new_posting&username=$user_name&userPST=$user_PST'>Create a new blog post</a>";
	 
    }
}


sub action_edit_posting() {

    $attributes{POST_TITLE} = $post;
    $attributes{USERPST} = $user_name;
    
    foreach my $temp (sort glob "$data_dir/*.$user_name.$blog.*.post_title") {
        my $buffer = markup_to_HTML(read_file("${temp}"));
        if ($post =~ $buffer){
           $temp =~ s/_title$//;
		   $attributes{POST_CONTENT} = markup_to_HTML(read_file("${temp}"));
		}
    }		
    print get_html_template("edit_posting.post.template");
}

sub action_edit_commenting() {  

    my $location = param('location');
    $attributes{LOCATION} = $location;
    
    $attributes{COMMENT} = read_file("${location}");
		
    print get_html_template("edit_commenting.post.template");
}

sub action_comment_posting() {

    save_comment() if defined param(new_comment);
    save_edit_comment() if defined param(edit_comment);
    delete_coment() if defined param(delete_comment);    
   
    my $tempPostTitle = $post;
       $tempPostTitle =~ s/\s+/_/g;
    
   foreach my $comment (sort glob "$data_dir/*.$blog.$tempPostTitle.*.comment") {

		$attributes{COMMENT} = markup_to_HTML(read_file($comment));
		$comment =~ /(\d{12})\W+([^\W]*).*/;
		$attributes{TIME} = $1;
		$attributes{PEOPLE} = $2;
		$people = $attributes{PEOPLE};
					
		print get_html_template("display_comment.post.template");	
		if($user_name eq $people){
		    $attributes{LOCATION} = $comment;
		    print get_html_template("print_comment_delete.template");
		    print get_html_template("print_comment_edit.template");		    
        }
	}
}


sub create_blog() {
    $user_PST = $user_name;
    $attributes{USER} = $user_name;
    $attributes{USERPST} = $user_name;
    $blog =~ s/[^0-9A-Za-z_]//g;
    param('blog', $blog);
    
    my $sameblog = 0;
    
    foreach my $temp (sort glob "$data_dir/*.*.blog_title") {

       $temp =~ /$data_dir\/[^.]*.([^.]*).blog_title/;
       my $blogName = $1;
       
        if ($blog =~ $blogName){
           print "<p><font color=\'red\'><b>blog name already exists,change another one</b></font><p>";
           $sameblog = 1;
           print "</ul><p><a href='$url?action=list_blogs&username=$user_name'>go Back</a>";
           exit(1);
       }
       
       if (param(new_blog_title) =~ read_file("${temp}")){
           print "<p><font color=\'red\'><b>blog Title already exists,change another one</b></font><p>";
           $sameblog = 1;
           print "</ul><p><a href='$url?action=list_blogs&username=$user_name'>go Back</a>";
           exit(1);
       }
    }
    if(!$sameblog){ 
    	my $nbt = param(new_blog_title);
    	$nbt =~ s/</lt/g;
   		$nbt =~ s/>/gt/g;   
	    write_file("$data_dir/$user_name.$blog.blog_title", $nbt);
    }
}


sub save_regist(){
    my $user_name = param(username);
       if($user_name =~ /[^0-9A-Za-z_]/){
           print "<p><font color=\'red\'><b>regist failed invalid 
                        User name caractor only use 0-9 A-Z a-z _</b></font><p>";
           print "<p><a href='$url?action=register'>Register again</a><br>";
           exit(1);
       }
    my $file = sprintf "$user_name.information";


    if(!check_user_name_exists(param(username))){
        my $password = param(password);
           if($password =~ /[^0-9A-Za-z_]/){
                print "<p><font color=\'red\'><b>regist failed invalid 
                        password caractor only use 0-9 A-Z a-z _</b></font><p>";
                print "<p><a href='$url?action=register'>Register again</a><br>";
                exit(1);
            }
        my $email = param(email);

           if( $email !~ /[A-Z0-9a-z._]*@[A-Z0-9a-z._]*/){
                print "<p><font color=\'red\'><b>regist failed invalid 
                        email address.</b></font><p>";
                print "<p><a href='$url?action=register'>Register again</a><br>";
                exit(1);
            } 
	    write_file("$data_dir/temp/$file", $password);
	    write_file("$data_dir/temp/${file}_email", $email);	    
	}else{
        print "<p><font color=\'red\'><b>username already exist change another one</b></font><p>";
        print "<p><a href='$url?action=register'>Register again</a><br>";
		exit(1);		
	}

}

sub delete_post() {

    $attributes{POST_TITLE} = $post;
    $attributes{USERPST} = $user_name;
    
    foreach my $temp (sort glob "$data_dir/*.$user_name.$blog.*.post_title") {
        my $buffer = markup_to_HTML(read_file("${temp}"));
        if ($post =~ $buffer){          
		   `rm $temp`;
		    $temp =~ s/_title$//;
		   `rm $temp`;
		   print "deleted $buffer";
		}
    }
    
    my $tempPostTitle = $post;
       $tempPostTitle =~ s/\s+/_/g;
 
    foreach my $temp (sort glob "$data_dir/*.*.$blog.$tempPostTitle.*.comment") {
	    $temp =~ s/\s//g;
	    `rm $temp`;                                   #remove all the comment with this post
	}	      		
}

sub delete_coment(){
    my $location = param(location);  
    print "comment deleted<p>";
	`rm $location`;
}

sub save_posting() {
	
    my $time = `date +%Y%m%d%H%M`;
	my $last_post = max(map(/(\d+).post$/, glob("$data_dir/*.$user_name.$blog.*.post")));

	my $file = sprintf "$time.$user_name.$blog.%d.post", ($last_post || 0) + 1;
	   $file =~ s/\s*//g;

    my $tempContents = param(new_posting_contents);
    $tempContents =~ s/</lt/g;
    $tempContents =~ s/>/gt/g; 
    my $tempTitle = param(new_posting_title);
    $tempTitle =~ s/</lt/g;
    $tempTitle =~ s/>/gt/g;   
    if(!check_post_title_exists($tempTitle)){

	    write_file("$data_dir/$file", $tempContents);
	    write_file("$data_dir/${file}_title", $tempTitle);
	}else{
	    $attributes{POST_TITLE} = $tempTitle;       
		$attributes{POST_CONTENT} = $tempContents;
		print get_html_template("rename.template");
		exit(0);		
	}
}


sub save_edit_comment() {
    my $location = param(location);
    my $tempComment = param(edit_comment);

    $tempComment =~ s/</lt/g;
    $tempComment =~ s/>/gt/g;            
	write_file("$location", $tempComment);		        
     
}

sub save_edit_posting() {


    my $post = $attributes{POST_TITLE};
    foreach my $temp (sort glob "$data_dir/*.$user_name.$blog.*.post_title"){
        my $buffer = markup_to_HTML(read_file("${temp}"));
        if ($post =~ $buffer){
           $temp =~ s/_title$//;           
           write_file("${temp}", param(edit_posting_contents));
		}
    }		
}




sub check_post_title_exists($) {
    my ($title) = @_;
    foreach my $temp (sort glob "$data_dir/*.$user_name.$blog.*.post_title") {
        my $buffer = markup_to_HTML(read_file("${temp}"));
        if ($title =~ /^$buffer$/){
            return 1;     
        }
	}
    return 0;
}


sub check_user_name_exists($) {
    my ($user_name) = @_;
    foreach my $temp (sort glob "$data_dir/*.information") {        
        $temp =~ s/\.\/data\///;
        $temp =~ s/\.information//;
        if ($user_name =~ /^$temp$/){
            return 1;     
        }
	}
    return 0;
}

sub check_password_correct($) {
    my ($user_name) = @_;
    if (param(username) eq '' || param(password) eq ''){
         return 0;
    }
    
    my $password = read_file("$data_dir/$user_name.information");

    if ($password eq param(password)){
        return 1;
    }
    
    return 0;
}



sub save_comment(){

    my $tempPostTitle = $post;
       $tempPostTitle =~ s/\s+/_/g;
    my $time = `date +%Y%m%d%H%M`;
 
	my $last_comment = max(map(/(\d+).comment/, glob("$data_dir/*.$blog.$tempPostTitle.*.comment"))); 
	my $file = sprintf "$time.$user_name.$blog.$tempPostTitle.%d.comment",($last_comment || 0) + 1;
	$file =~ s/\s//g;
	
	my $cmt = param(new_comment);
		$cmt =~ s/</lt/g;
		$cmt =~ s/>/gt/g;
	write_file("$data_dir/$file", $cmt);		
}


sub markup_to_HTML($) {
	my ($text) = @_;
	$text =~ s/\[(\/?[bius])\]/<$1>/gi;
	
	$text =~ s/\[url\]([^\[]*)\[\/url\]/<a href='$1'>$1<\/a>/gi;	
	$text =~ s/\[url=([^\[]*)\]([^\[]*)\[\/url\]/<a href='$1'>$2<\/a>/gi;	

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




sub get_html_template($) {
	my ($file) = @_;
	return "" if !-r $file;   					#<p><font color=\"white\"><b>MISSING TEMPLATE BUT Thats allright $file</b></font><p>
	my $html = read_file($file);
	$html =~ s/\$(\w+)/defined $attributes{$1} ? $attributes{$1} : "\$$1"/eg;
	return  "<!-- $file begin -->\n$html<!-- $file end -->\n";
}

sub read_file($) {
	my ($file) = @_;
    open(my $f, '<', $file) or return undef;
    return do {local $/; <$f>}
}

sub write_file($$) {
	my ($file, $contents) = @_;
    open my $f, '>', $file or die "Can not write '$file': $!";
    print $f $contents if defined $f;
}
