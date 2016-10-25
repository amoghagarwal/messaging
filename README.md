
1) To start the python app:                python manage.py runserver 0.0.0.0:8000 (already running) 

2) To start the Processing Service:        python manage.py process_message (already running)

3) To start the Callback Retry Service:    python manage.py retry_mechanism (already running)

4) To start Redis server:                  redis_server (already running)

5) To view RabbitMQ queue status:          52.91.72.147:15672/

6) API to hit:                             POST http://52.91.72.147:8000/message_api/ PARAM: Message : <string>, Url: <callback_url>

7) Callback Success                        http://52.91.72.147:8000/test_api_success/

8) Callback Failure                        http://52.91.72.147:8000/test_api_failure/

9) Landing Page                            http://52.91.72.147:8000/

10) Redis entries                          redis-cli -n <db>

