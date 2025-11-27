"""Web server entry point for Personal AI."""

from personal_ai.web import run_web_server

if __name__ == "__main__":
    import sys
    
    host = "127.0.0.1"
    port = 5000
    debug = False
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--debug":
            debug = True
        elif sys.argv[1].isdigit():
            port = int(sys.argv[1])
    
    run_web_server(host=host, port=port, debug=debug)

