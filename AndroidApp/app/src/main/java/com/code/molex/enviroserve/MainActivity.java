package com.code.molex.enviroserve;

import android.graphics.Color;
import android.support.design.widget.Snackbar;
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
import com.jjoe64.graphview.GraphView;
import com.jjoe64.graphview.helper.DateAsXAxisLabelFormatter;
import com.jjoe64.graphview.series.DataPoint;
import com.jjoe64.graphview.series.LineGraphSeries;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {
    private final String errorString = "Error parsing JSON";


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        populateGraph();
    }


    @Override
    protected void onResume(){{
        super.onResume();
        refreshData(getWindow().getDecorView().getRootView());
    }

    }

    private void populateGraph(){
        // Get data
        RequestQueue queue = Volley.newRequestQueue(this);
        String url = "http://192.168.1.250:2020/climate/data";

        JsonObjectRequest dataRequest = new JsonObjectRequest
                (Request.Method.GET, url, null, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        try {
                            Log.i("Graph", "Graphing data...");
                            JSONArray data = (JSONArray) response.get("results");
                            DataPoint[] tempPoints = new DataPoint[data.length()];
                            DataPoint[] humidPoints = new DataPoint[data.length()];
                            DataPoint[] pressurePoints = new DataPoint[data.length()];

                            for (int i=0; i < data.length(); i++){
                                JSONObject datapoint = data.getJSONObject(i);
                                Date dataAge = new Date((long) datapoint.getDouble("time")*1000);

                                tempPoints[i] = new DataPoint(dataAge,
                                                              datapoint.getDouble("temp"));
                                humidPoints[i] = new DataPoint(dataAge,
                                                               datapoint.getDouble("humid"));
                                pressurePoints[i] = new DataPoint(dataAge,
                                                                  datapoint.getDouble("pressure"));
                            }

                            LineGraphSeries<DataPoint> tempSeries = new LineGraphSeries<>(tempPoints);
                            tempSeries.setColor(Color.RED);
                            LineGraphSeries<DataPoint> humidSeries = new LineGraphSeries<>(humidPoints);
                            humidSeries.setColor(Color.CYAN);
                            LineGraphSeries<DataPoint> pressureSeries = new LineGraphSeries<>(pressurePoints);
                            pressureSeries.setColor(Color.GREEN);

                            // Get Add the series to the graph
                            GraphView graph = findViewById(R.id.graph);

                            // set date label formatter
                            graph.getGridLabelRenderer().setLabelFormatter(new DateAsXAxisLabelFormatter(MainActivity.this));
                            graph.getGridLabelRenderer().setNumHorizontalLabels(3); // only 4 because of the space

                            // Enable scroll and zoom
                            // set manual X bounds
                            graph.getViewport().setYAxisBoundsManual(true);
                            graph.getViewport().setMinY(30);
                            graph.getViewport().setMaxY(50);
                            Log.i("Graph x bounds",
                                    "From: " + Double.toString(tempPoints[0].getX()) +
                                            " To: " + Double.toString(tempPoints[tempPoints.length-1].getX()));
                            Double firstPoint = tempPoints[tempPoints.length-1].getX() - (24 * 3600 * 1000);
                            graph.getViewport().setMinX(firstPoint);
                            graph.getViewport().setMaxX(tempPoints[tempPoints.length-1].getX());
                            graph.getViewport().setXAxisBoundsManual(true);
                            // Human rounding: nice y axis, bad x axis
                            // No human rounding: nice axis. bad y axis
                            graph.getGridLabelRenderer().setHumanRounding(true);

                            // enable scaling and scrolling
                            graph.getViewport().setScalable(true);
                            graph.getViewport().setScalableY(true);

                            graph.addSeries(tempSeries);
                            graph.addSeries(humidSeries);

                            // Add pressure and sort it's axis
                            graph.getSecondScale().addSeries(pressureSeries);
                            graph.getSecondScale().setMinY(950);
                            graph.getSecondScale().setMaxY(1050);
                            graph.getGridLabelRenderer().setVerticalLabelsSecondScaleColor(Color.GREEN);
                        } catch (JSONException e){
                            // TODO: Something clever
                        }
                    }
                }, new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {

                    }
                });
        queue.add(dataRequest);
    }

    public HashMap<String, String> formatData(JSONObject response) throws JSONException{
        HashMap<String, String> data = new HashMap<>();
        // Extract data from JSON
        Long temperature = Math.round(response.getDouble("temp"));
        Long humidity = Math.round(response.getDouble("humid"));
        Long pressure = Math.round(response.getDouble("pressure"));
        // Format it
        data.put("temp", temperature.toString() + getString(R.string.temp_unit));
        data.put("humid", humidity.toString() + getString(R.string.humid_unit));
        data.put("pressure", pressure.toString() + getString(R.string.pressure_unit));
        return data;

    }

    public void refreshData(View view){
        // Get text placeholders
        final TextView tempText = findViewById(R.id.temp);
        final TextView humidText = findViewById(R.id.humid);
        final TextView pressureText = findViewById(R.id.pressure);
        final TextView dateHolder = findViewById(R.id.date_holder);

        // Prepare for sending request
        RequestQueue queue = Volley.newRequestQueue(this);
        // TODO: Don't hardcode the URL
        String url = "http://192.168.1.250:2020/climate/now";

        JsonObjectRequest dataRequest = new JsonObjectRequest
                (Request.Method.GET, url, null, new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        try{
                            // Extract values from JSON
                            Log.i("Response content", response.toString());
                            HashMap<String, String> data = formatData(response);
                            // Set text boxes
                            tempText.setText(data.get("temp"));
                            humidText.setText(data.get("humid"));
                            pressureText.setText(data.get("pressure"));
                            // Set data age string
                            String dateFormat = "dd/MM/yy hh:mm";
                            SimpleDateFormat formatter = new SimpleDateFormat(dateFormat, Locale.getDefault());
                            Date dataAge = new Date((long) response.getDouble("time")*1000);
                            dateHolder.setText(formatter.format(dataAge));
                        } catch (JSONException e) {
                            // TODO: Show a dialog box
                            tempText.setText(errorString);
                        }
                    }
                }, new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        // Code here.
                        Snackbar warningSnack = Snackbar.make(findViewById(R.id.root),
                                R.string.connectionWarningString, Snackbar.LENGTH_LONG);
                        warningSnack.show();
                    }
                });
        // Tell the user what's going on
        Snackbar connectingSnack = Snackbar.make(findViewById(R.id.root),
                R.string.server_connecting_message, Snackbar.LENGTH_SHORT);
        connectingSnack.show();
        // Send request
        queue.add(dataRequest);
    }
}
