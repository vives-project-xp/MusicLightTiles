class Pixel {
  int red = 0;
  int green = 0;
  int blue = 0;
  int white = 0;

  // Default constructor
  Pixel();
  // Constructor from RGBW values
  Pixel.fromrgbw(this.red, this.green, this.blue, this.white);
  // Constructor from dictionary (JSON)
  factory Pixel.fromJson(Map<String, dynamic> json) {
    return Pixel()
      ..red = json['r']
      ..green = json['g']
      ..blue = json['b']
      ..white = json['w'];
  }

  // Function to convert Pixel object to dictionary
  Map<String, dynamic> toJson() => {
        'r': red,
        'g': green,
        'b': blue,
        'w': white,
      };
}