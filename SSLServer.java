import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.security.KeyStore;


import javax.net.ssl.KeyManager;
import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLServerSocket;
import javax.net.ssl.SSLServerSocketFactory;
import javax.net.ssl.SSLSession;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;

public class SSLServer {
	private int port = 9999;
	private boolean isServerDone = false;
	
	SSLServer() { }
	SSLServer(int port) { this.port = port; }
	
	
	private SSLContext createSSLContext() {
		String keystoreFilename = "D:\\Uni\\CITS3002\\keystore.jks";
		char[] storepass = "password".toCharArray();
		char[] keypass = storepass;
		String alias = "selfsigned";
		
		try {
			KeyStore keyStore = KeyStore.getInstance("JKS");
			keyStore.load(new FileInputStream(keystoreFilename), storepass);
			
			// Create key manager
			KeyManagerFactory kmf = KeyManagerFactory.getInstance("SunX509");
			kmf.init(keyStore, keypass);
			KeyManager[] km = kmf.getKeyManagers();
			
			// Create trust manager
			TrustManagerFactory trustManagerFactory = TrustManagerFactory.getInstance("SunX509");
            trustManagerFactory.init(keyStore);
            TrustManager[] tm = trustManagerFactory.getTrustManagers();
            
         // Initialize SSLContext
            SSLContext sslContext = SSLContext.getInstance("TLSv1");
            sslContext.init(km,  tm, null);
            
            return sslContext;
		}
		catch (Exception ex) {
			// Error handiling
		}
		
		return null;
	}

	public void run() {
		SSLContext sslContext = this.createSSLContext();
		
		try {
			SSLServerSocketFactory sslServerSocketFactory = sslContext.getServerSocketFactory();
            
            // Create server socket
            SSLServerSocket sslServerSocket = (SSLServerSocket) sslServerSocketFactory.createServerSocket(this.port);
             
            System.out.println("SSL server started");
            while(!isServerDone){
                SSLSocket sslSocket = (SSLSocket) sslServerSocket.accept();
                 
                // Start the server thread
                new ServerThread(sslSocket).start();
            }
		}
		catch (Exception ex) {
			// Error handle
		}
	}
	
	// Thread handling the socket 
	static class ServerThread extends Thread {
		private SSLSocket sslSocket = null;
		
		ServerThread(SSLSocket sslSocket) {
			this.sslSocket = sslSocket;
		}
		
		public void run() {
			sslSocket.setEnabledCipherSuites(sslSocket.getSupportedCipherSuites());
            
            try{
                // Start handshake
                sslSocket.startHandshake();
                 
                // Get session after the connection is established
                SSLSession sslSession = sslSocket.getSession();
                 
                System.out.println("SSLSession :");
                System.out.println("\tProtocol : "+sslSession.getProtocol());
                System.out.println("\tCipher suite : "+sslSession.getCipherSuite());
                 
                // Start handling application content
                InputStream inputStream = sslSocket.getInputStream();
                OutputStream outputStream = sslSocket.getOutputStream();
                 
                BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream));
                PrintWriter printWriter = new PrintWriter(new OutputStreamWriter(outputStream));
                 
                String line = null;
                while((line = bufferedReader.readLine()) != "ahh"){
                    System.out.println("Inut : "+line);
                     
                    if(line.trim().isEmpty()){
                        //break;
                    	System.out.println("Empty line");
                    }
                }
                 
                // Write data
                printWriter.print("HTTP/1.1 200\r\n");
                
                printWriter.flush();
                 
                sslSocket.close();
            } catch (Exception ex) {
                ex.printStackTrace();
            }
		}
	}
}

