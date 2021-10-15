using Microsoft.Bonsai.SimulatorApi.Client;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Microsoft.Bonsai.Api.Samples.Cartpole
{
    public class Model : IModel
    {

        // simulation constants
        static double GRAVITY = 9.8; // a classic...
        static double CART_MASS = 0.31; // 1.0; // kg
        static double POLE_MASS = 0.055; // 0.1; // kg
        static double TOTAL_MASS = CART_MASS + POLE_MASS;
        static double POLE_HALF_LENGTH = 0.4 / 2; // 1.0/2.; half the pole's length in m
        static double POLE_MASS_LENGTH = POLE_MASS * POLE_HALF_LENGTH;
        static double FORCE_MAG = 1.0; // 10.0
        static double STEP_DURATION = 0.02; // seconds between state updates (20ms)
        static double TRACK_WIDTH = 1.0; // m
        static double FORCE_NOISE = 0.02; // % of FORCE_MAG

        internal double cart_position;
        internal double cart_velocity;
        internal double pole_angle;
        internal double pole_angular_velocity;
        internal double pole_center_position;
        internal double pole_center_velocity;
        internal double target_pole_position;

        public Model() 
        {

        }

        public void Reset()
        {
            cart_position = 0;
            cart_velocity = 0;
            pole_angle = 0;
            pole_angular_velocity = 0;
            pole_center_position = 0;
            target_pole_position = 0;
        }

        public void Start(Config config)
        {
            Reset();

            //use values from config to set initial conditions (if applicable)
        }

        public void Step(Action action)
        {
            double command = action.Command;

            double min = -0.02;
            double max = 0.02;

            double rand = min + (new Random().NextDouble() * (max - min));

            // simulation for a cart and a pole
            double force = FORCE_MAG * (command + rand); //command == 1 ? FORCE_MAG : -FORCE_MAG;
            double cosTheta = Math.Cos(pole_angle);
            double sinTheta = Math.Sin(pole_angle);

            double temp = (force + POLE_MASS_LENGTH * Math.Pow(pole_angular_velocity, 2) * sinTheta) / TOTAL_MASS;
            double angularAcceleration = (GRAVITY * sinTheta - cosTheta * temp)
                    / (POLE_HALF_LENGTH * (4.0 / 3.0 - (POLE_MASS * Math.Pow(cosTheta, 2)) / TOTAL_MASS));

            double linearAcceleration = temp - (POLE_MASS_LENGTH * angularAcceleration * cosTheta) / TOTAL_MASS;

            cart_position = cart_position + STEP_DURATION * cart_velocity;
            cart_velocity = cart_velocity + STEP_DURATION * linearAcceleration;

            pole_angle = pole_angle + STEP_DURATION * pole_angular_velocity;
            pole_angular_velocity = pole_angular_velocity + STEP_DURATION * angularAcceleration;

            //use the pole center, not the cart center, for tracking
            pole_center_position = cart_position + Math.Sin(pole_angle) * POLE_HALF_LENGTH;
            pole_center_velocity = cart_velocity + Math.Sin(pole_angular_velocity) * POLE_HALF_LENGTH;
        }

        public object State { get { return new State(this); } }
        public bool? Halted {
            get
            {
                return Math.Abs(pole_angle) >= Math.PI / 2;
            }
        }
    }
}
