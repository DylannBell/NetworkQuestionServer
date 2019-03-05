import java.io.*;
import java.net.InetSocketAddress;
import java.net.MalformedURLException;
import java.lang.*;
import java.net.URL;
import java.security.KeyStore;

import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.TrustManagerFactory;

import com.sun.net.httpserver.*;

import javax.net.ssl.SSLEngine;
import javax.net.ssl.SSLParameters;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.Reader;
import java.net.URLConnection;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

import java.security.cert.X509Certificate;
import java.util.List;
import java.util.Map.Entry;
import java.util.Scanner;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.net.InetAddress;

import com.sun.net.httpserver.*;

public class HTTPS_Server {
	int port;
	int maxClients;
	String keystorePass = "password";
	String keystoreLocation = "D:\\Uni\\CITS3002\\keystore.jks";
	
	ConcurrentHashMap<String, String> sessions;
	
	public HTTPS_Server(int port, int maxClients) {
		this.port = port;
		this.maxClients = maxClients;
		sessions = new ConcurrentHashMap<>();
	}

	public void start() throws Exception {

		try {
			
			// Create socket address
			InetSocketAddress address = new InetSocketAddress(port);

			// Initialise HTTPS Server
			HttpsServer httpsServer = HttpsServer.create(address, 0);
			SSLContext sslContext = SSLContext.getInstance("TLS");

			// Keystore
			char[] password = keystorePass.toCharArray();
			KeyStore ks = KeyStore.getInstance("JKS");
			
			FileInputStream fis = new FileInputStream(keystoreLocation);
			ks.load(fis, password);

			// Setup key manager factory
			KeyManagerFactory kmf = KeyManagerFactory.getInstance("SunX509");
			kmf.init(ks, password);

			// Setup trust manager factory
			TrustManagerFactory tmf = TrustManagerFactory.getInstance("SunX509");
			tmf.init(ks);

			// Setup HTTPS context and parameters
			sslContext.init(kmf.getKeyManagers(), tmf.getTrustManagers(), null);
			httpsServer.setHttpsConfigurator(new HttpsConfigurator(sslContext) {
				public void configure(HttpsParameters params) {
					try {
						
						// Initialise SSL context
						SSLContext c = SSLContext.getDefault();
						SSLEngine engine = c.createSSLEngine();
						params.setNeedClientAuth(false);
						params.setCipherSuites(engine.getEnabledCipherSuites());
						params.setProtocols(engine.getEnabledProtocols());

						// get the default parameters
						SSLParameters defaultSSLParameters = c.getDefaultSSLParameters();
						params.setSSLParameters(defaultSSLParameters);

					}
					catch (Exception ex) {
						System.out.println("Failed to create HTTPS port");
					}
				}
			});
			
			// Manage context handlers 
			httpsServer.createContext("/test", new TestHandler());
			
			// Set the default executor to a multi-threaded executor allowing an amount of clients
			// Search up the params on this threadpoolexecutor
			httpsServer.setExecutor(new ThreadPoolExecutor(4, 8, 30, TimeUnit.SECONDS, new ArrayBlockingQueue<Runnable>(maxClients)));
			httpsServer.start();
			System.out.println("Server started on port: " + port);		

		}
		catch (Exception exception) {
			System.out.println("Failed to create HTTPS server on port " + port + " of localhost");
			exception.printStackTrace();

		}
	}

	private void makeGetRequest(String URL) throws Exception {
		
		// Disable certificate validation because our certficates are self-signed, if this was production, obvs wouldn't do this.
		// http://www.nakov.com/blog/2009/07/16/disable-certificate-validation-in-java-ssl-connections/
		
		// Create a trust manager that does not validate certificate chains
        TrustManager[] trustAllCerts = new TrustManager[] {new X509TrustManager() {
                public java.security.cert.X509Certificate[] getAcceptedIssuers() {
                    return null;
                }
                public void checkClientTrusted(X509Certificate[] certs, String authType) {
                }
                public void checkServerTrusted(X509Certificate[] certs, String authType) {
                }
            }
        };
 
        // Install the all-trusting trust manager
        SSLContext sc = SSLContext.getInstance("SSL");
        sc.init(null, trustAllCerts, new java.security.SecureRandom());
        HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
 
        // Create all-trusting host name verifier
        HostnameVerifier allHostsValid = new HostnameVerifier() {
            public boolean verify(String hostname, SSLSession session) {
                return true;
            }
        };
 
        // Install the all-trusting host verifier
        HttpsURLConnection.setDefaultHostnameVerifier(allHostsValid);
		
		URL url = new URL(URL);
		HttpsURLConnection connection = (HttpsURLConnection)url.openConnection(); // No proxy
		
		if(connection == null) {
			throw new Exception("Unable to connect.");
			// TODO: better error handiling
		}
		
		// Read the contents, print them out to console for now
		BufferedReader br = new BufferedReader(new InputStreamReader(connection.getInputStream()));
		String input;
		
		while((input = br.readLine()) != null) {
			System.out.println(input);
		}
		
		br.close();
		
	}

	
	
	
	/* 
	 * Handlers
	 */
	private static class TestHandler implements HttpHandler {
		/*
		 * Handle the "/test" directory, which will just be used for random testing
		 * This will not be active in the final product.
		 */
			public void handle(HttpExchange t) throws IOException {
				HttpsExchange httpsExchange = (HttpsExchange) t;
				
				// Read the incoming request's body
				InputStream inStream = httpsExchange.getRequestBody();
				Scanner s = new Scanner(inStream).useDelimiter("\\A");
				String body = s.hasNext() ? s.next() : "";

				// Send response
				String responseText = "This is the response from this server.";
				t.getResponseHeaders().add("Access-Control-Allow-Origin", "*");
				t.sendResponseHeaders(200, responseText.length());
				OutputStream os = t.getResponseBody();
				os.write(responseText.getBytes());
				os.close();
				
				System.out.println("______________________\n");
				
			}
		}

	private static class LoginHandler implements HttpHandler {
		/*
		 * Handles the "/login" directory which will be used to send a POST request to login.
		 * Handle the authentication, session managment etc.
		 */
		public void handle(HttpExchange t) throws IOException {
			HttpsExchange httpsExchange = (HttpsExchange) t;
			

		}
		
	}


}