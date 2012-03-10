#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>

#define PORT 12345

int
make_socket (uint16_t port)
{
  int sock, flag = 1;
  struct sockaddr_in name;

  /* Create the socket. */
  sock = socket(PF_INET, SOCK_DGRAM, 0);
  if (sock < 0)
    {
      perror("socket");
      exit(EXIT_FAILURE);
    }

  /* Set the reuse flag. */
  if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &flag, sizeof(flag)) < 0)
    {
      perror("setsockopt(SOL_SOCKET, SO_REUSEADDR)");
      exit(EXIT_FAILURE);
    }

  /* Give the socket a name. */
  name.sin_family = AF_INET;
  name.sin_port = htons(port);
  name.sin_addr.s_addr = htonl(INADDR_ANY);
  if (bind(sock, (struct sockaddr *) &name, sizeof (name)) < 0)
    {
      perror("bind");
      exit(EXIT_FAILURE);
    }

  return sock;
}

int
main(void)
{
  int sock, new;
  struct sockaddr_in clientname;
  unsigned char buf[256];
  socklen_t size;

  sock = make_socket(PORT);

  fprintf(stderr, "Receiving on port %d\n", PORT);

  if (recv(sock, buf, sizeof(buf), MSG_PEEK) < 0)
    {
      perror("recv");
      exit(EXIT_FAILURE);
    }

  size = sizeof(clientname);
  new = accept(sock, (struct sockaddr *) &clientname, &size);
  if (new < 0)
    {
      perror("accept");
      exit(EXIT_FAILURE);
    }

  fprintf(stderr, "Connect from %s:%hu\n",
	  inet_ntoa(clientname.sin_addr),
	  ntohs(clientname.sin_port));

  if (read(new, buf, 1) < 0)
    {
      perror("read");
      exit(EXIT_FAILURE);
    }

  fprintf(stderr, "Byte received: 0x%x\n", buf[0]);

  close(new);
  close(sock);

  exit(EXIT_SUCCESS);
}
