import cv2
import csv
import imutils
import numpy as np
import os
import pandas as pd
import shutil

def omr_calculation():
    def get_main_countours(image):
        cnts = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        docCnt = []
        # ensure that at least one contour was found
        if len(cnts) > 0:
            # sort the contours according to their size in
            # descending order
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
            # loop over the sorted contours
            for c in cnts:
                # approximate the contour
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                # if our approximated contour has four points,
                # then we can assume we have found the paper
                if len(approx) == 4:
                    docCnt.append(approx)
        return docCnt


    def get_bird_eye_view(image, cont):
        def order_points(pts):
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            return rect

        def four_point_transform(image, pts):
            rect = order_points(pts)
            (tl, tr, br, bl) = rect
            widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
            maxWidth = max(int(widthA), int(widthB))
            heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
            maxHeight = max(int(heightA), int(heightB))
            dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
            return warped

        warped = four_point_transform(image, cont.reshape(4, 2))
        return warped


    def get_enrollment_id_and_test_id(image):
        thresh = cv2.adaptiveThreshold(
        image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 77, 10)
        thresh = thresh[60:, :]
        enroll_id = []
        test_id = []
        enroll_id_sec = thresh[:, :225]
        test_id_sec = thresh[:, 225:]
        temp1 = enroll_id_sec.copy()
        temp1 = temp1[:-10, 20:-5]
        width = temp1.shape[1]
        height = temp1.shape[0]
        for i in range(10):
            found_index = []
            filled_ratios = []
            for j in range(10):
                t = temp1[int(j * height / 10):int((j + 1) * height / 10), int(i * width / 10):int((i + 1) * width / 10)]
                erode_kernel = np.array([[1, 0, 1], [1, 0, 1], [1, 0, 1]]).astype(np.uint8)
                t = cv2.erode(t, erode_kernel.astype(np.uint8), iterations=3)
                filled_ratios.append(np.sum(t / 255.0) / (t.shape[0] * t.shape[1]))
            if sum(filled_ratios) == 0:
                enroll_id.append(found_index)
                continue
            filled_ratios_norm = filled_ratios / (sum(filled_ratios))
            for i, ratio in enumerate(filled_ratios_norm):
                if (ratio > 0.1):
                    found_index.append((i + 1) % 10)
            enroll_id.append(found_index)

        temp1 = test_id_sec.copy()
        temp1 = temp1[:-10, 30:-15]
        width = temp1.shape[1]
        height = temp1.shape[0]
        for i in range(5):
            found_index = []
            filled_ratios = []
            for j in range(10):
                t = temp1[int(j * height / 10):int((j + 1) * height / 10), int(i * width / 5):int((i + 1) * width / 5)]
                erode_kernel = np.array([[1, 0, 1], [1, 0, 1], [1, 0, 1]]).astype(np.uint8)
                t = cv2.erode(t, erode_kernel.astype(np.uint8), iterations=3)
                filled_ratios.append(np.sum(t / 255.0) / (t.shape[0] * t.shape[1]))
            if (sum(filled_ratios) == 0):
                test_id.append(found_index)
                continue
            filled_ratios_norm = filled_ratios / (sum(filled_ratios))
            for i, ratio in enumerate(filled_ratios_norm):
                if (ratio > 0.1):
                    found_index.append((i + 1) % 10)
            test_id.append(found_index)
        return enroll_id, test_id


    def get_marks_section_1(image):
        def get_section_ans(inp):
            ans_marked = []
            temp1 = inp.copy()
            width = temp1.shape[1]
            height = temp1.shape[0]
            for i in range(5):
                found_index = []
                filled_ratios = []
                for j in range(4):
                    t = temp1[int(i * height / 5) + 10:int((i + 1) * height / 5) - 10,
                        int(j * width / 4):int((j + 1) * width / 4)]
                    erode_kernel = np.array([[1, 0, 1], [1, 0, 1], [1, 0, 1]]).astype(np.uint8)
                    t = cv2.erode(t, erode_kernel.astype(np.uint8), iterations=3)
                    filled_ratios.append(np.sum(t / 255.0) / (t.shape[0] * t.shape[1]))
                if (sum(filled_ratios) == 0):
                    ans_marked.append(found_index)
                    continue
                filled_ratios_norm = filled_ratios / (sum(filled_ratios))
                for i, ratio in enumerate(filled_ratios_norm):
                    if (ratio > 0.1):
                        found_index.append((i + 1))
                ans_marked.append(found_index)
            return ans_marked

        thresh = cv2.adaptiveThreshold(
            image[55:, :], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 77, 10)

        thresh1 = thresh[:, 25:110]
        thresh2 = thresh[:, 165:-30]
        ans_marked = []
        ans_marked.extend(get_section_ans(thresh1))
        ans_marked.extend(get_section_ans(thresh2))
        return ans_marked


    def get_marks_section_2(image):
        def get_section_ans(inp):
            ans_marked = []
            temp1 = inp.copy()
            width = temp1.shape[1]
            height = temp1.shape[0]
            for i in range(2):
                found_index = []
                filled_ratios = []
                for j in range(4):
                    t = temp1[int(i * height / 2) + 5:int((i + 1) * height / 2) - 15,
                        int(j * width / 4):int((j + 1) * width / 4)]
                    erode_kernel = np.array([[1, 0, 1], [1, 0, 1], [1, 0, 1]]).astype(np.uint8)
                    t = cv2.erode(t, erode_kernel.astype(np.uint8), iterations=3)
                    filled_ratios.append(np.sum(t / 255.0) / (t.shape[0] * t.shape[1]))
                if (sum(filled_ratios) == 0):
                    ans_marked.append(found_index)
                    continue
                filled_ratios_norm = filled_ratios / (sum(filled_ratios))
                for i, ratio in enumerate(filled_ratios_norm):
                    if (ratio > 0.1 and filled_ratios[i] > 0.05):
                        found_index.append(i + 1)
                ans_marked.append(found_index)
            return ans_marked

        thresh = cv2.adaptiveThreshold(
            image[30:, :], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 77, 10)

        thresh1 = thresh[:, 20:100]
        thresh2 = thresh[:, 160:240]
        thresh3 = thresh[:, 300:380]
        thresh4 = thresh[:, 435:515]
        thresh5 = thresh[:, 575:655]
        ans_marked = []
        ans_marked.extend(get_section_ans(thresh1))
        ans_marked.extend(get_section_ans(thresh2))
        ans_marked.extend(get_section_ans(thresh3))
        ans_marked.extend(get_section_ans(thresh4))
        ans_marked.extend(get_section_ans(thresh5))
        return ans_marked


    def main(image_path):
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        edged = cv2.Canny(blurred, 75, 200)

        main_contours = get_main_countours(edged)

        sections = []
        for cont in main_contours:
            warped = get_bird_eye_view(blurred, cont)
            if (warped.shape[0] < 50):
                continue
            sections.append(warped)

        enroll_id, test_id = get_enrollment_id_and_test_id(sections[0])
        ans_marked_section_1 = get_marks_section_1(sections[2])
        ans_marked_section_2 = get_marks_section_2(sections[1])
        ans_marked = []
        ans_marked.extend(ans_marked_section_1)
        ans_marked.extend(ans_marked_section_2)
        return {
            "enroll_id": enroll_id,
            "test_id": test_id,
            "ans_marked": ans_marked
        }

    filename = "ans" + ".csv"
    filepath = os.path.join('static/result/', filename)

    with open(filepath, 'w', newline='') as file:
        csvwriter = csv.writer(file)
        fields = ['Enrollment Id', 'Score']
        csvwriter.writerow(fields, )

    total_img = os.listdir("static/omr_sheets/")
    for i in total_img:
        FILE_PATH = os.path.join(('static/omr_sheets/'), str(i))
        csv_file = os.listdir("static/answer")
        csv_path = "static/answer/" + str(csv_file[0])
        # print(csv_path)
        # column_names = ["qno", "answer", "marks"]
        df = pd.read_csv(csv_path)
        # print(df)
        qno = df.qno.to_list()
        # answer = [list(row) for row in df.answer]
        answer = [list(map(int, str(x).split(','))) for x in df.answer]
        marks = df.marks.to_list()

        # print(qno)

        print("Correct Answer")
        print(answer)

        # print(marks)

        values = main(FILE_PATH)
        ansmarked = values["ans_marked"]

        print("Ans Marked")
        print(ansmarked)

        enrollid = values['enroll_id']
        print(enrollid)

        towrite = []

        eid = ''
        score = 0
        # res = [''.join(str(ele)) for ele in enrollid]
        # print(enrollid[0][0])
        cnt = 0
        for q in range(len(enrollid)):
            # print(q,end='')
            if (len(enrollid[q]) == 1):
                eid = eid + str(enrollid[q][0])
            elif (len(enrollid[q])!=1):
                eid = eid+'_'
        print(eid)
        towrite.append(eid)
        curr = -1

        for q, r in zip(ansmarked, answer):
            curr = curr + 1
            # print(len(q),len(r))
            if len(q) == 0:
                continue
            else:
                if (len(q) == len(r)):
                    for c in range(len(q)):
                        # print(curr,c)
                        if (ansmarked[curr][c] != answer[curr][c]):
                            break
                        if(c==len(q)-1):
                            score = score + marks[curr]
        print(score)
        towrite.append(score)
        with open(filepath, 'a', newline='') as file:
            csvwriter = csv.writer(file)
            csvwriter.writerow(towrite, )
        os.remove(FILE_PATH)
    os.remove(csv_path)
# omr_calculation()

def omr_calculation_1():

    def get_main_countours(image):
        cnts = cv2.findContours(image, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        docCnt = []

        if len(cnts) > 0:

            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

            # loop over the sorted contours
            for c in cnts:
                # approximate the contour
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                # if our approximated contour has four points,
                # then we can assume we have found the paper
                if len(approx) == 4:
                    docCnt.append(approx)
        return docCnt


    def get_bird_eye_view(image, cont):
        def order_points(pts):
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            return rect

        def four_point_transform(image, pts):
            rect = order_points(pts)
            (tl, tr, br, bl) = rect
            widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
            maxWidth = max(int(widthA), int(widthB))
            heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
            maxHeight = max(int(heightA), int(heightB))
            dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
            return warped

        warped = four_point_transform(image, cont.reshape(4, 2))
        return warped


    def get_enrollment_id_andtest_id(image):
        thresh = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 77, 10)
        thresh = thresh[77:, :]
        # fig, ax = plt.subplots(figsize=(10,20))
        # plt.imshow(cv2.cvtColor(thresh, cv2.COLOR_BGR2RGB))
        # plt.show()

        enroll_id = []
        test_id = []
        enroll_id_sec = thresh[:, 14:378]
        test_id_sec = thresh[:, 440:]

        temp1 = enroll_id_sec.copy()
        temp1 = temp1[:-10, 32:-5]
        width = temp1.shape[1]
        height = temp1.shape[0]

        for i in range(10):
            found_index = []
            filled_ratios = []
            for j in range(10):
                t = temp1[int(j * height / 10):int((j + 1) * height / 10), int(i * width / 10):int((i + 1) * width / 10)]
                erode_kernel = np.array([[1, 0, 1], [1, 0, 1], [1, 0, 1]]).astype(np.uint8)
                t = cv2.erode(t, erode_kernel.astype(np.uint8), iterations=3)
                filled_ratios.append(np.sum(t / 255.0) / (t.shape[0] * t.shape[1]))
            if sum(filled_ratios) == 0:
                enroll_id.append(found_index)
                continue
            filled_ratios_norm = filled_ratios / (sum(filled_ratios))
            for i, ratio in enumerate(filled_ratios_norm):
                if (ratio > 0.1):
                    found_index.append((i + 1) % 10)
            enroll_id.append(found_index)

        temp1 = test_id_sec.copy()
        temp1 = temp1[:-10, 30:-15]
        width = temp1.shape[1]
        height = temp1.shape[0]
        for i in range(5):
            found_index = []
            filled_ratios = []
            for j in range(10):
                t = temp1[int(j * height / 10):int((j + 1) * height / 10), int(i * width / 5):int((i + 1) * width / 5)]
                erode_kernel = np.array([[1, 0, 1], [1, 0, 1], [1, 0, 1]]).astype(np.uint8)
                t = cv2.erode(t, erode_kernel.astype(np.uint8), iterations=3)
                filled_ratios.append(np.sum(t / 255.0) / (t.shape[0] * t.shape[1]))
            if (sum(filled_ratios) == 0):
                test_id.append(found_index)
                continue
            filled_ratios_norm = filled_ratios / (sum(filled_ratios))
            for i, ratio in enumerate(filled_ratios_norm):
                if (ratio > 0.1):
                    found_index.append((i + 1) % 10)
            test_id.append(found_index)
        return enroll_id, test_id


    def get_marks_section_1(image):
        def get_section_ans(inp):
            ans_marked = []
            temp1 = inp.copy()
            width = temp1.shape[1]
            height = temp1.shape[0]
            for i in range(5):
                found_index = []
                filled_ratios = []
                # fig, axs = plt.subplots(1, 4)
                for j in range(4):
                    t = temp1[int(i * height / 5) + 10:int((i + 1) * height / 5) - 10,
                        int(j * width / 4):int((j + 1) * width / 4)]
                    #   fig, ax = plt.subplots(figsize=(10,20))
                    #   axs[j].imshow(cv2.cvtColor(t, cv2.COLOR_BGR2RGB))
                    #   plt.show()
                    erode_kernel = np.array([[1, 0, 1], [1, 0, 1], [1, 0, 1]]).astype(np.uint8)
                    t = cv2.erode(t, erode_kernel.astype(np.uint8), iterations=3)
                    # axs[j].imshow(cv2.cvtColor(t, cv2.COLOR_BGR2RGB))
                    filled_ratios.append(np.sum(t / 255.0) / (t.shape[0] * t.shape[1]))
                #             plt.show()
                if (sum(filled_ratios) == 0):
                    ans_marked.append(found_index)
                    continue
                filled_ratios_norm = filled_ratios / (sum(filled_ratios))
                for i, ratio in enumerate(filled_ratios_norm):
                    if (ratio > 0.1):
                        found_index.append((i + 1))
                ans_marked.append(found_index)
            return ans_marked

        thresh = cv2.adaptiveThreshold(
            image[105:, :], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 77, 10)

        thresh1 = thresh[:, 70:200]

        thresh2 = thresh[:, 262:395]

        ans_marked = []
        ans_marked.extend(get_section_ans(thresh1))
        ans_marked.extend(get_section_ans(thresh2))
        return ans_marked


    def get_marks_section_2(image):
        def get_section_ans(inp):
            ans_marked = []
            temp1 = inp.copy()
            width = temp1.shape[1]
            height = temp1.shape[0]
            for i in range(4):
                found_index = []
                filled_ratios = []
                # fig, axs = plt.subplots(1, 4)
                for j in range(4):
                    t = temp1[int(i * height / 4) + 5*i :int((i + 1) * height / 4) - 20,
                        int(j * width / 4):int((j + 1) * width / 4)]
                    # fig, ax = plt.subplots(figsize=(10,20))
                    # axs[j].imshow(cv2.cvtColor(t, cv2.COLOR_BGR2RGB))
                    # plt.show()
                    erode_kernel = np.array([[1, 0, 1], [1, 0, 1], [1, 0, 1]]).astype(np.uint8)
                    t = cv2.erode(t, erode_kernel.astype(np.uint8), iterations=3)
                    # axs[j].imshow(cv2.cvtColor(t, cv2.COLOR_BGR2RGB))
                    filled_ratios.append(np.sum(t / 255.0) / (t.shape[0] * t.shape[1]))

                if sum(filled_ratios) == 0:
                    ans_marked.append(found_index)
                    continue
                filled_ratios_norm = filled_ratios / (sum(filled_ratios))
                for i, ratio in enumerate(filled_ratios_norm):
                    if ratio > 0.1 and filled_ratios[i] > 0.05:
                        found_index.append(i + 1)
                ans_marked.append(found_index)
            return ans_marked

        thresh = cv2.adaptiveThreshold(
            image[50:, :], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 77, 10)

        thresh1 = thresh[:, 45:175]
        thresh2 = thresh[:, 270:404]
        thresh3 = thresh[:, 496:628]
        thresh4 = thresh[:, 723:856]
        thresh5 = thresh[:, 950:1083]
        ans_marked = []
        ans_marked.extend(get_section_ans(thresh1))
        ans_marked.extend(get_section_ans(thresh2))
        ans_marked.extend(get_section_ans(thresh3))
        ans_marked.extend(get_section_ans(thresh4))
        ans_marked.extend(get_section_ans(thresh5))
        return ans_marked

    def main(FILE_PATH):

        image = cv2.imread(FILE_PATH)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        edged = cv2.Canny(blurred, 75, 200)

        main_contours = get_main_countours(edged)

        sections = []
        for cont in main_contours:
            warped = get_bird_eye_view(blurred, cont)
            if warped.shape[0] < 75:
                continue
            sections.append(warped)

        enroll_id, test_id = get_enrollment_id_andtest_id(sections[1])
        # print(enroll_id)
        # print(test_id)

        ans_marked_section_1 = get_marks_section_1(sections[2])
        # print(ans_marked_section_1)
        ans_marked_section_2 = get_marks_section_2(sections[0])
        # print(ans_marked_section_2)
        ans_marked = []
        ans_marked.extend(ans_marked_section_1)
        ans_marked.extend(ans_marked_section_2)
        return {
            "enroll_id": enroll_id,
            "test_id": test_id,
            "ans_marked": ans_marked
        }
    filename = "ans" + ".csv"
    filepath = os.path.join('static/result/', filename)

    with open(filepath, 'w', newline='') as file:
        csvwriter = csv.writer(file)
        fields = ['Enrollment Id', 'Score']
        csvwriter.writerow(fields, )
    total_img = os.listdir("static/omr_sheets/")

    for i in total_img:
        FILE_PATH = os.path.join(('static/omr_sheets/'), str(i))
        csv_file = os.listdir("static/answer/")
        csv_path = "static/answer/" + str(csv_file[0])
        df = pd.read_csv(csv_path)
        answer = [list(map(int, str(x).split(','))) for x in df.answer]
        marks = df.marks.to_list()
        print("Correct Answer")
        print(answer)
        values = main(FILE_PATH)
        ansmarked = values["ans_marked"]
        print("Ans Marked")
        print(ansmarked)
        enrollid = values['enroll_id']
        print(enrollid)

        towrite = []
        eid = ''
        score = 0
        cnt = 0
        for q in range(len(enrollid)):
            # print(q,end='')
            if (len(enrollid[q]) == 1):
                eid = eid + str(enrollid[q][0])
            elif (len(enrollid[q]) != 1):
                eid = eid + '_'
        print(eid)
        towrite.append(eid)
        curr = -1

        for q, r in zip(ansmarked, answer):
            curr = curr + 1
            # print(len(q),len(r))
            if len(q) == 0:
                continue
            else:
                if (len(q) == len(r)):
                    for c in range(len(q)):
                        # print(curr,c)
                        if (ansmarked[curr][c] != answer[curr][c]):
                            break
                        if (c == len(q) - 1):
                            score = score + marks[curr]
        print(score)
        towrite.append(score)
        with open(filepath, 'a', newline='') as file:
            csvwriter = csv.writer(file)
            csvwriter.writerow(towrite, )
        os.remove(FILE_PATH)
    os.remove(csv_path)
