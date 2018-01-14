package com.code.molex.enviroserve;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    public void refreshData(View view){
        TextView tempText = findViewById(R.id.temp);
        String TempMessage = "292 'C";
        tempText.setText(TempMessage);

        TextView humidText = findViewById(R.id.humid);
        String humidMessage = "100 %";
        humidText.setText(humidMessage);

        TextView pressureText = findViewById(R.id.pressure);
        String pressureMessage = "1525 Millibar";
        pressureText.setText(pressureMessage);
    }
}
