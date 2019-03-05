import os
import javabridge

with javabridge.vm(run_headless=True):
    print (javabridge.run_script('java.lang.String.format("Hello, %s!", greetee);',
                                dict(greetee='world')))



