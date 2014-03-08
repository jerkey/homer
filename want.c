#include <stdio.h>
int main(){
char buff[BUFSIZ];
FILE *fp = popen("python need.py 123 456","r");
while ( fgets( buff, BUFSIZ, fp ) != NULL ) {
  printf("%s", buff );
}
pclose(fp);
return (0);
}

