import math

class PreProcessor():
    def str_to_points(self, point):
        plist = []
        for p in point.split('+'):
            splited = p.split(',')
            if splited[0] == '' :
                splited = splited[1:]

            size = len(splited)
            stroke = []

            if size > 1 :
                for i in range(0, size, 3):
                    if splited[i] != '' :
                        if size < i+3:
                            raise RuntimeError("Given sign data's format is invalid.\nThe data should consist of x, y and time which is continously repeated")

                        try:
                            x = float(splited[i])
                            y = float(splited[i+1])
                            time = float(splited[i+2])

                            pts = { "x": x, "y": y, "time": time }
                            stroke.append(pts)
                        except ValueError:
                            raise RuntimeError("The x, y and time data should be integer data.")
                
                plist.append(stroke)

        return plist

    def resample(self, points, nunber_of_clouds):
        newPoints = []

        for stroke in points:
            I = self.path_length(stroke) / (nunber_of_clouds-1)
            D = 0

            _stroke = []
            _stroke.append(stroke[0]) # 초기값

            for i in range(1, len(stroke)):

                p1 = stroke[i]
                p2 = stroke[i-1]
                d = self.distance(p1, p2)

                if round((D + d),10) >= round(I,10) :  # 마지막에 소수점 13번째 자리수에서 미세한 값이 달라 소수점자리수를 10자리까지 올려서 오류 해결
                    if d != 0 :
                        _p = {}
                        _p['x'] = p2['x'] + ((I-D)/d)*(p1['x']-p2['x'])
                        _p['y'] = p2['y'] + ((I-D)/d)*(p1['y']-p2['y'])
                        _p['time'] = p1['time']
                        _stroke.append(_p)

                        D = (D+d)-I

                else :
                    D = D+d

            newPoints.append(_stroke)

        return newPoints

    def path_length(self, points):
        d = 0
        for i in range(1, len(points)):
            p1 = points[i]
            p2 = points[i - 1]

            d = d + self.distance(p1, p2)

        return d

    def scale(self, points):
        plist = []
        min_time = points[0][0]['time']

        _x = points[0][0]['x']
        _y = points[0][0]['y']        

        for stroke in points:
            _stroke = []
            for p in stroke:
                _p = {}
                _p['x'] = p['x'] - _x
                _p['y'] = p['y'] - _y
                _p['time'] = p['time'] - min_time
                _stroke.append(_p)
            
            plist.append(_stroke)

        return plist

    def normalize(self, points):
        maxX = points[0][0]['x']
        maxY = points[0][0]['y']

        for stroke in points:
            for p in stroke:
                if p['x'] > maxX:
                    maxX = p['x']
                
                if p['y'] > maxY:
                    maxY = p['y']
        
        plist = []
        for stroke in points:
            _stroke = []
            for p in stroke:
                _p = {}
                _p['x'] = p['x'] / maxX
                _p['y'] = p['y'] / maxY
                _p['time'] = p['time']
                _stroke.append(_p)
            
            plist.append(_stroke)
        
        return plist

    def distance(self, p1, p2):
        return math.sqrt((p2['x'] - p1['x'])**2 + (p2['y'] - p1['y'])**2)

    def speed(self,points):
        speed = []

        for stroke in points:

            D = self.path_length(stroke)
            time = stroke[len(stroke)-1]-stroke[2]
            sp = D/time
            speed.append(sp)

        return speed

class FinoSign():
    def evaluate(self, sign1, sign2):
        preprocessor = PreProcessor()
        sign1 = preprocessor.str_to_points(sign1)
        sign1 = preprocessor.scale(sign1)
        sign1 = preprocessor.resample(sign1, 10)
        sign1 = preprocessor.normalize(sign1)

        sign2 = preprocessor.str_to_points(sign2)
        sign2 = preprocessor.scale(sign2)
        sign2 = preprocessor.resample(sign2, 10)
        sign2 = preprocessor.normalize(sign2)

        distance = self.cloud_distance(sign1, sign2)
        print(distance)

        return distance

    def distance(self, p1, p2):
        return math.sqrt((p2['x'] - p1['x'])**2 + (p2['y'] - p1['y'])**2)

    def cloud_distance(self, sign1, sign2):
        distance = 0

        for i in range(len(sign1)):
            for j in range(len(sign1[i])):
                distance = distance + self.distance(sign1[i][j], sign2[i][j])
        
        return distance