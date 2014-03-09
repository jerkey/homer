#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

int main()
{
    int fd;
    char *a_pipe = "/tmp/a_pipe";
    mkfifo(a_pipe, 0666); /*fifo as modified by current creation mask*/
    fd = open(a_pipe, O_WRONLY);
    write(fd, "test", sizeof("test"));
    close(fd);
    unlink(a_pipe);
    return 0;
}
/*
int test(){
char buff[BUFSIZ];
FILE *fp = popen("python need.py 123 456","r");
while ( fgets( buff, BUFSIZ, fp ) != NULL ) {
  printf("%s", buff );
}
pclose(fp);
return (0);
}
*/
