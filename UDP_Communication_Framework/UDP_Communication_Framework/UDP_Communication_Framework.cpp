// UDP_Communication_Framework.cpp : Defines the entry point for the console application.
//

#pragma comment(lib, "ws2_32.lib")
#include "stdafx.h"
#include <winsock2.h>
#include "ws2tcpip.h"
#include <stdint.h>
#include <string.h>
#include <string>

#define TARGET_IP	"147.32.221.18"

#define BUFFERS_LEN 1024


#define SENDER
#ifdef SENDER
#define TARGET_PORT 5020
#define LOCAL_PORT 5002
#endif // SENDER

//#define RECEIVER
#ifdef RECEIVER
#define TARGET_PORT 5002
#define LOCAL_PORT 5020
#endif // RECEIVER


void InitWinsock()
{
	WSADATA wsaData;
	WSAStartup(MAKEWORD(2, 2), &wsaData);
}

//**********************************************************************
int main()
{
	SOCKET socketS;
	InitWinsock();
	
	struct sockaddr_in local;
	struct sockaddr_in from;
	
	int fromlen = sizeof(from);
	local.sin_family = AF_INET;
	local.sin_port = htons(LOCAL_PORT);
	local.sin_addr.s_addr = INADDR_ANY;
	
	
	socketS = socket(AF_INET, SOCK_DGRAM, 0);
	if (bind(socketS, (sockaddr*)&local, sizeof(local)) != 0){
		printf("Binding error!\n");
	    getchar(); //wait for press Enter
		return 1;
	}
	//**********************************************************************
	
	char buffer_rx[BUFFERS_LEN];
	char buffer_tx[BUFFERS_LEN];
	
	char* const file_name = "send_txt.txt";
	//printf("enter_file:");
	//scanf("%s", &file_name);
	FILE *opened_file = fopen(file_name, "rb");
	if (!opened_file) {
		exit(100);
	}
	
	//uint32_t position = 0;

	while (!feof(opened_file)) {
		char file_line[BUFFERS_LEN];
		fread(file_line, sizeof(char), BUFFERS_LEN, opened_file);

	#ifdef SENDER
	
		sockaddr_in addrDest;
		addrDest.sin_family = AF_INET;
		addrDest.sin_port = htons(TARGET_PORT);
		InetPton(AF_INET, _T(TARGET_IP), &addrDest.sin_addr.s_addr);

		//memcpy((void*)buffer_tx, (void*)&position, sizeof(uint32_t));
		strncpy(buffer_tx, file_line, BUFFERS_LEN); //put some data to buffer

		printf("Sending packet.\n");
		sendto(socketS, buffer_tx, 1024, 0, (sockaddr*)&addrDest, sizeof(addrDest));	
	}
	closesocket(socketS);
	#endif // SENDER

#ifdef RECEIVER
	
	char position[4];

	while (1) {
		strncpy(buffer_rx, "No data received.\n", BUFFERS_LEN);
		printf("Waiting for datagram ...\n");
		if (recvfrom(socketS, position, sizeof(position), 0, (sockaddr*)&from, &fromlen) == SOCKET_ERROR) && recvfrom(socketS, buffer_rx, sizeof(buffer_rx), 0, (sockaddr*)&from, &fromlen) == SOCKET_ERROR) {
			printf("Socket error!\n");
			getchar();
			return 1;
		}
		else {
			printf("Datagram: %s", buffer_rx);
			getchar();
		}
	}

	closesocket(socketS);
#endif
	//**********************************************************************

	getchar(); //wait for press Enter
	return 0;
}
