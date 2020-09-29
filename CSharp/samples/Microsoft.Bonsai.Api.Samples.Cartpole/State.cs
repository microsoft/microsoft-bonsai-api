using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Microsoft.Bonsai.Api.Samples.Cartpole
{
    public class State
    {

        public double cart_position;
        public double cart_velocity;
        public double pole_angle;
        public double pole_angular_velocity;
        public double pole_center_position;
        public double pole_center_velocity;
        public double target_pole_position;

        public State()
        {

        }

        public State(Model cp)
        {
            cart_position = cp.cart_position;
            cart_velocity = cp.cart_velocity;
            pole_angle = cp.pole_angle;
            pole_angular_velocity = cp.pole_angle;
            pole_center_position = cp.pole_angle;
            pole_center_velocity = cp.pole_angle;
            target_pole_position = cp.pole_angle;
        }
    }
}
