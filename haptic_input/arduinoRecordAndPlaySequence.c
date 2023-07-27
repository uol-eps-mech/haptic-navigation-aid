int arr[5];
unsigned long time1 = 0;
int debounce = 200;
int counter = 0;
int record_count = 0;

int button[4] = {2, 4, 6, 8};
int leds[4] = {3, 5, 7, 9};

void setup()
{
    // set buttons to be inputs and leds to be outputs
    for (int i = 0; i < 5; i++)
    {
        pinMode(button[i], INPUT);
        pinMode(leds[i], OUTPUT);
    }
    for (int n = 0; n < 10; n++)
        arr[n] = 7; // initialize seqeuence array to empty
    Serial.begin(9600);
}

void turn_off_leds()
{
    for (int i = 0; i < 5; i++)
    {
        digitalWrite(leds[i], LOW);
    }
}

// Function to print the current sequence through Serial
void print_sequence()
{
    Serial.println("-----------------------");
    Serial.println("Sequence:");
    for (int i = 0; i < 5; i++)
    {
        Serial.print(arr[i]);
    }
    Serial.println();
    Serial.println("-----------------------");
}

// Function to play back the recorded sequence using LEDs
void play_sequence()
{
    print_sequence();
    for (int i = 0; i < 5; i++)
    {
        if (arr[i] != 7)
        {
            digitalWrite(leds[arr[i]], HIGH);
            delay(500);
            digitalWrite(leds[arr[i]], LOW);
            delay(500);
        }
    }
    counter = 0;
}

void record_sequence()
{
    boolean mode = digitalRead(button[0]) || digitalRead(button[1]) || digitalRead(button[2]) || digitalRead(button[3]);

    // wait here till one of the pushbutton goes high;
    while (mode == LOW && record_count <= 1)
    {

        mode = digitalRead(button[0]) || digitalRead(button[1]) || digitalRead(button[2]) || digitalRead(button[3]);
        if (mode == HIGH && millis() - time1 > debounce)
        {

            // find out which one is high and store that value in array;

            /*
             * EXAMPLE CASE for single button.
             * Add additional readings to check additional buttons
             */
            if (digitalRead(button[0]))
            {
                arr[counter] = 0;            // set the button 3 to the current index
                digitalWrite(leds[0], HIGH); // turn on the respective LED
                delay(500);                  // briefly turn on LED to show which button was pressed
                turn_off_leds();             // make sure all LEDs are OFF
                Serial.println("Button 1");
            }

            else if (digitalRead(button[1]))
            {
                arr[counter] = 1;            // set the button 1 to the current index
                digitalWrite(leds[1], HIGH); // turn on the respective LED
                delay(500);                  // briefly turn on LED to show which button was pressed
                turn_off_leds();             // make sure all LEDs are OFF
                Serial.println("Button 2");
            }

            else if (digitalRead(button[2]))
            {
                arr[counter] = 2;            // set the button 2 to the current index
                digitalWrite(leds[2], HIGH); // turn on the respective LED
                delay(500);                  // briefly turn on LED to show which button was pressed
                turn_off_leds();             // make sure all LEDs are OFF
                Serial.println("Button 3");
            }

            else if (digitalRead(button[3]))
            {
                arr[counter] = 3;            // set the button 0 to the current index
                digitalWrite(leds[3], HIGH); // turn on the respective LED
                delay(500);                  // briefly turn on LED to show which button was pressed
                turn_off_leds();             // make sure all LEDs are OFF
                Serial.println("Button 4");
            }

            else
                Serial.println("No button clicked");
            ;

            // print the value and the index;
            Serial.print(arr[counter]);
            Serial.print(" Stored in index: ");
            Serial.println(counter);

            if (counter < 4)
            {
                counter = (counter + 1);
            }
            else
            { // wait for PLAY PRESS?
                delay(1000);
                play_sequence();
            }

            // update value of time1 for button debouncing
            time1 = millis();
        }
    }
}

// The main loop that runs continuously
void loop()
{
    // Record the user's button presses and store them in the array
    record_sequence();
}
