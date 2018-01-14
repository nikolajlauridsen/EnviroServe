package com.code.molex.enviroserve;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

public class MainActivity extends AppCompatActivity {
    private final String errorString = "Error";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    public void refreshData(View view){
        final TextView tempText = findViewById(R.id.temp);
        final TextView humidText = findViewById(R.id.humid);
        final TextView pressureText = findViewById(R.id.pressure);

        RequestQueue queue = Volley.newRequestQueue(this);
        String url = "http://192.168.1.250:2020/climate/now";

        JsonObjectRequest dataRequest = new JsonObjectRequest
                (Request.Method.GET, url, null, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        try{
                            // Extract values from JSON
                            Log.i("Response content", response.toString());
                            Long temperature = Math.round(response.getDouble("temp"));
                            Long humidity = Math.round(response.getDouble("humid"));
                            Long pressure = Math.round(response.getDouble("pressure"));
                            String tempString = temperature.toString() + getString(R.string.temp_unit);
                            String humidString = humidity.toString() + getString(R.string.humid_unit);
                            String pressureString = pressure.toString() + getString(R.string.pressure_unit);
                            Log.i("Temp String", tempString);
                            Log.i("Humid String", humidString);
                            Log.i("Pressure String", pressureString);
                            // Set text boxes
                            tempText.setText(tempString);
                            humidText.setText(humidString);
                            pressureText.setText(pressureString);
                        } catch (JSONException e) {
                            tempText.setText(errorString);
                        }

                    }
                }, new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {

                    }
                });

        queue.add(dataRequest);
    }
}
